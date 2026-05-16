#!/bin/bash

set -e

BASE_DIR="$(pwd)/synth_models"
mkdir -p "$BASE_DIR"

echo "Téléchargement du modèle Piper dans $BASE_DIR ..."

curl -L \
  -o "$BASE_DIR/fr_FR-gilles-low.onnx" \
  "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/gilles/low/fr_FR-gilles-low.onnx"

curl -L \
  -o "$BASE_DIR/fr_FR-gilles-low.onnx.json" \
  "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/gilles/low/fr_FR-gilles-low.onnx.json"

echo "✔ Terminé"
echo "Modèle disponible dans : $BASE_DIR"
