#!/usr/bin/env bash
# =============================================================================
# mp3_to_wav.sh
# Convertit récursivement tous les fichiers MP3 d'un répertoire en WAV
# Format cible : PCM 16-bit signé, mono, 8000 Hz
#
# Usage : ./mp3_to_wav.sh <dossier_source> <dossier_sortie>
# =============================================================================

set -euo pipefail

# ── Couleurs ─────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# ── Aide ─────────────────────────────────────────────────────────────────────
usage() {
    echo -e "${CYAN}Usage :${NC} $0 <dossier_source> <dossier_sortie>"
    echo ""
    echo "  dossier_source   Répertoire contenant les fichiers MP3"
    echo "  dossier_sortie   Répertoire de destination (créé si inexistant)"
    echo ""
    echo "Exemple : $0 ./musiques ./wav_output"
    exit 1
}

# ── Vérification des arguments ────────────────────────────────────────────────
[[ $# -ne 2 ]] && usage

if [[ ! -d "$1" ]]; then
    echo -e "${RED}[ERREUR]${NC} Le dossier source '$1' n'existe pas."
    exit 1
fi

if ! command -v ffmpeg &>/dev/null; then
    echo -e "${RED}[ERREUR]${NC} ffmpeg n'est pas installé ou introuvable dans le PATH."
    exit 1
fi

# Résolution des chemins absolus
INPUT_DIR="$(cd "$1" && pwd)"
mkdir -p "$2"
OUTPUT_DIR="$(cd "$2" && pwd)"

# ── Compteurs ─────────────────────────────────────────────────────────────────
count_ok=0
count_err=0
count_skip=0

echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Conversion MP3 → WAV (PCM 16-bit, mono, 16 kHz)  ${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo -e "  Source  : ${INPUT_DIR}"
echo -e "  Sortie  : ${OUTPUT_DIR}"
echo -e "${CYAN}───────────────────────────────────────────────────${NC}"

# ── Boucle récursive sur tous les .mp3 ───────────────────────────────────────
# On utilise find -print (newline) + read, plus fiable que -print0
# sur les systèmes où le traitement des octets nuls est inconsistant.
while IFS= read -r mp3_file; do

    # Suppression du préfixe ./
    relative_path="${mp3_file#./}"

    mp3_abs="$INPUT_DIR/$relative_path"
    wav_relative="${relative_path%.[Mm][Pp]3}.wav"
    wav_file="$OUTPUT_DIR/$wav_relative"

    mkdir -p "$(dirname "$wav_file")"

    if [[ -f "$wav_file" ]]; then
        echo -e "  ${YELLOW}[IGNORÉ]${NC}  $relative_path (déjà converti)"
        count_skip=$((count_skip + 1))
        continue
    fi

    echo -e "  ${CYAN}[→]${NC} $relative_path"

    if ffmpeg -loglevel error \
              -i "$mp3_abs" \
              -ar 8000 \
              -ac 1 \
              -sample_fmt s16 \
              -c:a pcm_s16le \
              "$wav_file"; then
        echo -e "  ${GREEN}[OK]${NC} → $wav_relative"
        count_ok=$((count_ok + 1))
    else
        echo -e "  ${RED}[ERREUR]${NC} Échec de la conversion : $relative_path"
        [[ -f "$wav_file" ]] && rm -f "$wav_file"
        count_err=$((count_err + 1))
    fi

done < <(cd "$INPUT_DIR" && find . -type f -iname "*.mp3")

# ── Résumé ────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo -e "  ${GREEN}Convertis :${NC} $count_ok"
echo -e "  ${YELLOW}Ignorés   :${NC} $count_skip  (déjà existants)"
echo -e "  ${RED}Erreurs   :${NC} $count_err"
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"

[[ $count_err -gt 0 ]] && exit 1
exit 0
