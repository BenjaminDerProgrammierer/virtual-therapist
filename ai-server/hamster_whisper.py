#!/opt/asterisk-whisper/bin/python3
"""Near-live EAGI transcription for the Asterisk "call hamster" menu."""

from __future__ import annotations

import array
import asyncio
import io
import math
import os
import re
import select
import sys
import tempfile
import threading
import time
import wave
from dataclasses import dataclass, field
from pathlib import Path

import av
import numpy as np
import requests
from core import llm_request, tts_request
from db import Database
from faster_whisper import WhisperModel

SAMPLE_RATE = 16_000
MODEL_NAME = os.environ.get("HAMSTER_WHISPER_MODEL", "tiny")
MODEL_ROOT = "/opt/asterisk-whisper/models"
AI_SERVER_DIR = Path(__file__).resolve().parent
AI_ENV_FILE = Path("/etc/virtual-therapist/ai-server.env")
AI_AUDIO_LIMIT = 20 * 1024 * 1024
HAMSTER_ENDPOINT = "PJSIP/40202"
HAMSTER_RECORDING_DIR = Path("/var/spool/asterisk/monitor/hamster")
WHITE_NOISE_RMS = 225
WHITE_NOISE_LEAD_SECONDS = 0.75
WHITE_NOISE_TAIL_SECONDS = 1.0
MAX_SECONDS = 20.0
MIN_AUDIO_SECONDS = 1.5
PARTIAL_INTERVAL_SECONDS = 3.0
SPEECH_RMS = 500


class ChannelClosed(Exception):
    pass


class AGI:
    def __init__(self) -> None:
        self.environment: dict[str, str] = {}
        for raw_line in sys.stdin:
            line = raw_line.rstrip("\r\n")
            if not line:
                break
            key, separator, value = line.partition(":")
            if separator:
                self.environment[key.strip()] = value.strip()

    def command(self, command: str) -> str:
        sys.stdout.write(command + "\n")
        sys.stdout.flush()
        response = sys.stdin.readline()
        if not response:
            raise ChannelClosed
        return response.rstrip("\r\n")

    def verbose(self, message: str, level: int = 1) -> None:
        clean = " ".join(message.replace("\\", "/").replace('"', "'").split())
        self.command(f'VERBOSE "{clean[:1000]}" {level}')

    def wait_for_digit(self, timeout_ms: int) -> str:
        response = self.command(f"WAIT FOR DIGIT {timeout_ms}")
        marker = "result="
        if marker not in response:
            return ""
        result = response.split(marker, 1)[1].split()[0]
        try:
            value = int(result)
        except ValueError:
            return ""
        return chr(value) if value > 0 else ""

    def set_variable(self, name: str, value: str) -> None:
        clean = " ".join(value.replace("\\", "/").replace('"', "'").split())
        self.command(f'SET VARIABLE {name} "{clean}"')

    def stream_file(self, filename: str) -> None:
        clean = filename.replace("\\", "/").replace('"', "")
        self.command(f'STREAM FILE "{clean}" ""')

    def execute(self, application: str, arguments: str) -> str:
        safe_application = re.sub(r"[^A-Za-z0-9_]", "", application)
        clean_arguments = arguments.replace("\r", "").replace("\n", "")
        return self.command(f"EXEC {safe_application} {clean_arguments}")


@dataclass
class AudioCapture:
    fd: int = 3
    started_at: float = field(default_factory=time.monotonic)
    last_voice_at: float | None = None
    voiced_seconds: float = 0.0
    speech_seen: bool = False
    eof: bool = False
    chunks: list[bytes] = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock)
    stop_event: threading.Event = field(default_factory=threading.Event)

    def start(self) -> threading.Thread:
        thread = threading.Thread(
            target=self._read_loop, name="eagi-audio", daemon=True
        )
        thread.start()
        return thread

    def stop(self) -> None:
        self.stop_event.set()

    def snapshot(self) -> bytes:
        with self.lock:
            return b"".join(self.chunks)

    def duration(self) -> float:
        with self.lock:
            byte_count = sum(map(len, self.chunks))
        return byte_count / (SAMPLE_RATE * 2)

    def _read_loop(self) -> None:
        try:
            os.set_blocking(self.fd, False)
            while not self.stop_event.is_set():
                ready, _, _ = select.select([self.fd], [], [], 0.1)
                if not ready:
                    continue
                try:
                    chunk = os.read(self.fd, 8192)
                except BlockingIOError:
                    continue
                if not chunk:
                    self.eof = True
                    return
                if len(chunk) % 2:
                    chunk = chunk[:-1]
                if not chunk:
                    continue

                samples = array.array("h")
                samples.frombytes(chunk)
                if sys.byteorder != "little":
                    samples.byteswap()
                rms = math.sqrt(
                    sum(sample * sample for sample in samples) / len(samples)
                )
                chunk_seconds = len(chunk) / (SAMPLE_RATE * 2)
                now = time.monotonic()

                with self.lock:
                    self.chunks.append(chunk)
                    if rms >= SPEECH_RMS:
                        self.voiced_seconds += chunk_seconds
                        self.last_voice_at = now
                        if self.voiced_seconds >= 0.2:
                            self.speech_seen = True
        except OSError:
            self.eof = True


def transcribe(
    model: WhisperModel, audio_bytes: bytes, use_vad: bool
) -> tuple[str, str]:
    if len(audio_bytes) < int(MIN_AUDIO_SECONDS * SAMPLE_RATE * 2):
        return "", "unknown"

    audio = np.frombuffer(audio_bytes, dtype="<i2").astype(np.float32) / 32768.0
    segments, info = model.transcribe(
        audio,
        beam_size=1,
        best_of=1,
        condition_on_previous_text=False,
        vad_filter=use_vad,
        vad_parameters={"min_silence_duration_ms": 500} if use_vad else None,
    )
    text = " ".join(
        segment.text.strip() for segment in segments if segment.text.strip()
    )
    return " ".join(text.split()), info.language or "unknown"


def load_ai_environment() -> None:
    for raw_line in AI_ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == "REPLICATE_API_TOKEN":
            os.environ["REPLICATE_API_TOKEN"] = value.strip()
            return
    raise RuntimeError("REPLICATE_API_TOKEN is missing from the AI environment file")


def load_prompt(name: str) -> str:
    return (AI_SERVER_DIR / name).read_text(encoding="utf-8")


def get_phone_number(agi: AGI) -> str:
    caller_id = (
        agi.environment.get("agi_callerid")
        or agi.environment.get("agi_calleridnum")
        or agi.environment.get("callerid")
        or "anonymous"
    ).strip()
    if not caller_id or caller_id.lower().startswith("unknown"):
        return "anonymous"
    return caller_id


async def load_conversation_context(
    phone_number: str,
) -> tuple[int, int, list[dict[str, str]], str]:
    async with Database() as db:
        user_id = await db.get_user_id_from_phone_number(
            phone_number, create_if_not_exists=True
        )
        current_conversation_id = await db.get_latest_conversation_id(user_id=user_id)
        past_messages = await db.get_past_conversation_messages(
            conversation_id=current_conversation_id
        )
        memory = await db.get_user_memory(user_id=user_id)
    return user_id, current_conversation_id, past_messages, memory or ""


def build_chat_messages(
    system_prompt: str,
    memory: str,
    past_messages: list[dict[str, str]],
    transcript: str,
) -> list[dict[str, str]]:
    return (
        [
            {
                "role": "system",
                "content": system_prompt.format(memory=memory or "(no memory)"),
            }
        ]
        + past_messages
        + [{"role": "user", "content": transcript}]
    )


def build_memory_messages(
    memory_prompt: str, memory: str, transcript: str
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": memory_prompt.format(
                memory=memory
                or "No memory yet. Either add your first entries now or output this exact line not to add anything.",
                transcript=transcript,
            ),
        }
    ]


def download_as_slin(audio_url: str) -> str:
    response = requests.get(audio_url, timeout=(5, 60))
    response.raise_for_status()
    if len(response.content) > AI_AUDIO_LIMIT:
        raise RuntimeError("TTS audio response exceeded the size limit")

    output = tempfile.NamedTemporaryFile(
        mode="wb",
        prefix="hamster-ai-",
        suffix=".sln",
        dir="/tmp",
        delete=False,
    )
    output_path = output.name
    try:
        with output, av.open(io.BytesIO(response.content)) as container:
            resampler = av.AudioResampler(format="s16", layout="mono", rate=8000)
            for frame in container.decode(audio=0):  # type: ignore
                for converted in resampler.resample(frame):
                    output.write(
                        converted.to_ndarray().astype("<i2", copy=False).tobytes()
                    )
            for converted in resampler.resample(None):
                output.write(converted.to_ndarray().astype("<i2", copy=False).tobytes())
        if os.path.getsize(output_path) == 0:
            raise RuntimeError("TTS audio decoded to an empty file")
        return output_path
    except Exception:
        try:
            os.unlink(output_path)
        except FileNotFoundError:
            pass
        raise


def mix_with_white_noise(speech_path: str, noise_rms: int = WHITE_NOISE_RMS) -> str:
    speech = np.fromfile(speech_path, dtype="<i2").astype(np.int32)
    lead_samples = int(WHITE_NOISE_LEAD_SECONDS * 8000)
    tail_samples = int(WHITE_NOISE_TAIL_SECONDS * 8000)
    padded = np.pad(speech, (lead_samples, tail_samples))
    noise = np.random.default_rng().normal(0, noise_rms, padded.size).astype(np.int32)
    mixed = np.clip(padded + noise, -32768, 32767).astype("<i2")

    output = tempfile.NamedTemporaryFile(
        mode="wb",
        prefix="hamster-send-",
        suffix=".sln",
        dir="/tmp",
        delete=False,
    )
    with output:
        mixed.tofile(output)
    return output.name


def recording_base(agi: AGI) -> str:
    unique_id = agi.environment.get("agi_uniqueid", str(time.time_ns()))
    safe_id = re.sub(r"[^A-Za-z0-9_.-]", "_", unique_id)
    timestamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    return str(HAMSTER_RECORDING_DIR / f"{timestamp}-{safe_id}")


def wait_for_wav(path: str, minimum_seconds: float, timeout_seconds: float) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with wave.open(path, "rb") as recording:
                duration = recording.getnframes() / recording.getframerate()
            if duration >= minimum_seconds:
                return
        except (FileNotFoundError, EOFError, wave.Error, ZeroDivisionError):
            pass
        time.sleep(0.25)
    raise RuntimeError("timed out waiting for the hamster recording")


def transform_with_hamster(agi: AGI, speech_path: str) -> str:
    result_base = recording_base(agi)
    result_path = result_base + ".wav"
    mixed_path = mix_with_white_noise(speech_path, noise_rms=WHITE_NOISE_RMS)
    mixed_base = os.path.splitext(mixed_path)[0]
    monitor_base = mixed_base + "-monitor"
    playback_seconds = os.path.getsize(mixed_path) / (8000 * 2)
    response_wait_seconds = math.ceil(playback_seconds + 4)
    try:
        originate_arguments = (
            "Local/s@hamster-bridge/n,exten,hamster-playback,s,1,20,"
            f"v(HAMSTER_SEND={mixed_base}"
            f"^HAMSTER_MONITOR={monitor_base}"
            f"^HAMSTER_RESULT={result_base}"
            f"^HAMSTER_WAIT={response_wait_seconds})"
        )
        agi.verbose("HAMSTER TRANSFORM: calling endpoint 40202")
        agi.execute("Originate", originate_arguments)
        wait_for_wav(
            result_path,
            minimum_seconds=max(
                0.5, playback_seconds + response_wait_seconds - 0.5
            ),
            timeout_seconds=playback_seconds + response_wait_seconds + 10,
        )
        agi.verbose(f"HAMSTER RECORDING: accepting {result_path}")
        return result_base
    finally:
        for temporary_path in (mixed_path, monitor_base + ".wav"):
            try:
                os.unlink(temporary_path)
            except FileNotFoundError:
                pass


async def main() -> int:
    agi = AGI()
    capture = AudioCapture()

    try:
        agi.verbose("HAMSTER TRANSCRIPT: listening")
        reader = capture.start()
        model = WhisperModel(
            MODEL_NAME,
            device="cpu",
            compute_type="int8",
            cpu_threads=2,
            num_workers=1,
            download_root=MODEL_ROOT,
            local_files_only=True,
        )

        last_partial_at = time.monotonic()
        previous_partial = ""

        while True:
            now = time.monotonic()
            elapsed = now - capture.started_at
            if capture.eof or elapsed >= MAX_SECONDS:
                break

            if agi.wait_for_digit(100) == "#":
                agi.verbose("HAMSTER TRANSCRIPT: hash received, finishing")
                break

            if (
                capture.speech_seen
                and now - last_partial_at >= PARTIAL_INTERVAL_SECONDS
                and capture.duration() >= MIN_AUDIO_SECONDS
            ):
                partial, language = transcribe(model, capture.snapshot(), use_vad=False)
                if partial and partial != previous_partial:
                    agi.verbose(f"HAMSTER TRANSCRIPT [live/{language}]: {partial}")
                    previous_partial = partial
                last_partial_at = time.monotonic()

        capture.stop()
        reader.join(timeout=0.5)
        final_audio = capture.snapshot()
        final_text, language = transcribe(model, final_audio, use_vad=True)
        if not final_text and capture.speech_seen:
            agi.verbose(
                "HAMSTER TRANSCRIPT: VAD removed all speech, retrying without VAD"
            )
            final_text, language = transcribe(model, final_audio, use_vad=False)
        if not final_text and previous_partial:
            agi.verbose("HAMSTER TRANSCRIPT: using the last recognized live transcript")
            final_text = previous_partial
        if final_text:
            agi.verbose(f"HAMSTER TRANSCRIPT [final/{language}]: {final_text}")
            agi.stream_file("hamster-thinking")
            load_ai_environment()
            if str(AI_SERVER_DIR) not in sys.path:
                sys.path.insert(0, str(AI_SERVER_DIR))

            system_prompt = load_prompt("system.md")
            memory_prompt = load_prompt("memory.md")
            phone_number = get_phone_number(agi)
            user_id, current_conversation_id, past_messages, memory = (
                await load_conversation_context(phone_number)
            )
            chat_messages = build_chat_messages(
                system_prompt=system_prompt,
                memory=memory,
                past_messages=past_messages,
                transcript=final_text,
            )

            response_text = llm_request(chat_messages)
            audio_url = tts_request(response_text)
            agi.verbose(f"HAMSTER AI RESPONSE: {response_text}")
            audio_path = download_as_slin(audio_url)
            try:
                transformed_base = transform_with_hamster(agi, audio_path)
                agi.stream_file(transformed_base)
            finally:
                os.unlink(audio_path)

            memory_messages = build_memory_messages(
                memory_prompt=memory_prompt, memory=memory, transcript=final_text
            )
            memory_llm_response = llm_request(memory_messages)
            agi.verbose(f"MEMORY UPDATE: {memory_llm_response}")

            async with Database() as db:
                await db.save_message(
                    conversation_id=current_conversation_id,
                    role="user",
                    content=final_text,
                )
                await db.save_message(
                    conversation_id=current_conversation_id,
                    role="assistant",
                    content=response_text,
                )
                await db.update_user_memory(
                    user_id=user_id, new_memory=memory_llm_response
                )

            agi.set_variable("HAMSTER_AI_STATUS", "success")
        elif capture.speech_seen:
            agi.verbose(
                "HAMSTER TRANSCRIPT [final]: speech was detected but not recognized"
            )
            agi.set_variable("HAMSTER_AI_STATUS", "no-speech")
        else:
            agi.verbose("HAMSTER TRANSCRIPT [final]: no speech detected")
            agi.set_variable("HAMSTER_AI_STATUS", "no-speech")
        return 0
    except ChannelClosed:
        capture.stop()
        return 0
    except Exception as error:
        capture.stop()
        try:
            agi.verbose(f"HAMSTER TRANSCRIPT [error]: {type(error).__name__}: {error}")
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
