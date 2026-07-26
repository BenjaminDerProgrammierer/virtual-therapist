#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

if ((EUID != 0)); then
    echo "Run this script as root." >&2
    exit 1
fi

apt-get update
apt-get install -y curl libgomp1 openssl perl python3-venv sox

curl -fsSL https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz |
    tar -xz -C /opt
curl -fsSL -o /opt/piper/en_US-lessac-medium.onnx \
    https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
curl -fsSL -o /opt/piper/en_US-lessac-medium.onnx.json \
    https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
ln -sfn /opt/piper/piper /usr/local/bin/piper

python3 -m venv /opt/asterisk-whisper
/opt/asterisk-whisper/bin/pip install av faster-whisper numpy prisma python-dotenv requests
/opt/asterisk-whisper/bin/python - <<'PY'
from faster_whisper import WhisperModel
WhisperModel("tiny", device="cpu", compute_type="int8",
             download_root="/opt/asterisk-whisper/models")
PY

install -d /etc/asterisk /etc/virtual-therapist /var/lib/asterisk/agi-bin /opt/virtual-therapist
install -d /etc/systemd/system/asterisk.service.d
install -d /opt/asterisk-whisper/prisma-binaries
printf '[Service]\nRuntimeDirectory=asterisk\nEnvironmentFile=/etc/virtual-therapist/ai-server.env\nEnvironment=PRISMA_BINARY_CACHE_DIR=/opt/asterisk-whisper/prisma-binaries\n' \
    > /etc/systemd/system/asterisk.service.d/runtime.conf
systemctl daemon-reload
if [[ ! -s /etc/virtual-therapist/ai-server.env ]]; then
    read -rsp "Hack Club AI token: " hack_club_token
    echo
    install -o root -g asterisk -m 0640 /dev/null /etc/virtual-therapist/ai-server.env
    printf 'REPLICATE_API_TOKEN=%s\n' "${hack_club_token}" > /etc/virtual-therapist/ai-server.env
fi
if ! grep -q '^DATABASE_URL=' /etc/virtual-therapist/ai-server.env; then
    read -rsp "PostgreSQL URL: " database_url
    echo
    printf 'DATABASE_URL=%s\n' "${database_url}" >> /etc/virtual-therapist/ai-server.env
fi

database_url="$(awk -F= '$1 == "DATABASE_URL" {sub(/^[^=]*=/, ""); print; exit}' \
    /etc/virtual-therapist/ai-server.env)"

web_env="${repo_root}/virtual-therapist-app/.env"
if [[ ! -e "${web_env}" ]]; then
    web_owner="$(stat -c '%u' "${repo_root}/virtual-therapist-app")"
    web_group="$(stat -c '%g' "${repo_root}/virtual-therapist-app")"
    install -o "${web_owner}" -g "${web_group}" -m 0600 /dev/null "${web_env}"
else
    chmod 0600 "${web_env}"
fi

if ! grep -q '^DATABASE_URL=' "${web_env}"; then
    printf 'DATABASE_URL=%s\n' "${database_url}" >> "${web_env}"
fi
if ! grep -q '^BETTER_AUTH_SECRET=' "${web_env}"; then
    better_auth_secret="$(openssl rand -base64 32)"
    printf 'BETTER_AUTH_SECRET=%s\n' "${better_auth_secret}" >> "${web_env}"
fi
if ! grep -q '^BETTER_AUTH_URL=' "${web_env}"; then
    while true; do
        read -rp "Public-facing website URL (for example, https://therapy.example.com): " \
            public_url
        public_url="${public_url%/}"
        if [[ "${public_url}" =~ ^https?://[^[:space:]]+$ ]]; then
            break
        fi
        echo "Enter a complete URL beginning with http:// or https://." >&2
    done
    printf 'BETTER_AUTH_URL=%s\n' "${public_url}" >> "${web_env}"
fi

PATH="/opt/asterisk-whisper/bin:${PATH}" \
    PRISMA_BINARY_CACHE_DIR=/opt/asterisk-whisper/prisma-binaries \
    DATABASE_URL="${database_url}" \
    /opt/asterisk-whisper/bin/prisma generate \
    --schema "${repo_root}/ai-server/prisma/schema.prisma"

ln -sfn -- "${repo_root}"/asterisk-config/* /etc/asterisk/
ln -sfn -- "${repo_root}"/agi-bin/* /var/lib/asterisk/agi-bin/
ln -sfnT -- "${repo_root}/ai-server" /opt/virtual-therapist/ai-server

echo "Installation complete."
