#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

if ((EUID != 0)); then
    echo "Run this script as root." >&2
    exit 1
fi

apt-get update
apt-get install -y curl libgomp1 perl python3-venv sox

curl -fsSL https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz |
    tar -xz -C /opt
curl -fsSL -o /opt/piper/en_US-lessac-medium.onnx \
    https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
curl -fsSL -o /opt/piper/en_US-lessac-medium.onnx.json \
    https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
ln -sfn /opt/piper/piper /usr/local/bin/piper

python3 -m venv /opt/asterisk-whisper
/opt/asterisk-whisper/bin/pip install av faster-whisper numpy python-dotenv requests
/opt/asterisk-whisper/bin/python - <<'PY'
from faster_whisper import WhisperModel
WhisperModel("tiny", device="cpu", compute_type="int8",
             download_root="/opt/asterisk-whisper/models")
PY

install -d /etc/asterisk /etc/virtual-therapist /var/lib/asterisk/agi-bin /opt/virtual-therapist
install -d /etc/systemd/system/asterisk.service.d
printf '[Service]\nRuntimeDirectory=asterisk\n' > /etc/systemd/system/asterisk.service.d/runtime.conf
systemctl daemon-reload
if [[ ! -s /etc/virtual-therapist/ai-server.env ]]; then
    read -rsp "Hack Club AI token: " hack_club_token
    echo
    install -o root -g asterisk -m 0640 /dev/null /etc/virtual-therapist/ai-server.env
    printf 'REPLICATE_API_TOKEN=%s\n' "${hack_club_token}" > /etc/virtual-therapist/ai-server.env
fi

ln -sfn -- "${repo_root}"/asterisk-config/* /etc/asterisk/
ln -sfn -- "${repo_root}"/agi-bin/* /var/lib/asterisk/agi-bin/
ln -sfnT -- "${repo_root}/ai-server" /opt/virtual-therapist/ai-server

echo "Installation complete."
