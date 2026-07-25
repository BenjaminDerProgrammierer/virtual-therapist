# virtual-therapist

A hamster answering your therapy needs.

## Files

### Models and audio assets

- Faster-Whisper environment: /opt/asterisk-whisper/
- Whisper Tiny model directory: /opt/asterisk-whisper/models/
- Piper executable and libraries.
- en_US-lessac-medium.onnx
- en_US-lessac-medium.onnx.json
- Asterisk sound hamster-thinking in /var/lib/asterisk/sounds/

### Runtime directory

  /var/spool/asterisk/monitor/hamster/

  It must be writable by asterisk. Recordings and __pycache__ files are generated and do not
  need copying.

## Deploy

Run `sudo ./deploy-asterisk.sh` to install Piper and Faster-Whisper, then symlink the Asterisk
configuration, AGI scripts, and AI server runtime into their system directories.
