#!/bin/sh
set -e

echo "Téléchargement du modèle..."
mkdir -p synth_models

curl -L \
  -o "synth_models/fr_FR-gilles-low.onnx" \
  "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/gilles/low/fr_FR-gilles-low.onnx"

curl -L \
  -o "synth_models/fr_FR-gilles-low.onnx.json" \
  "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/gilles/low/fr_FR-gilles-low.onnx.json"


exec "$@"
