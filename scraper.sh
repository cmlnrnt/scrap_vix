#!/bin/bash

# URL de la page contenant les données du VIX
URL="https://www.boursorama.com/bourse/indices/cours/1cVIX/"

# Fichier CSV où les données seront enregistrées
OUTPUT="/home/ubuntu/scrap_vix/vix_data.csv"
LOG_FILE="/home/ubuntu/scrap_vix/debug_cron.log"
REPORT_FILE="/home/ubuntu/scrap_vix/daily_report.txt"

# Récupération de la page HTML
echo "[$(date)] Début du scraping" >> "$LOG_FILE"
PAGE_CONTENT=$(curl -s "$URL")

# Extraction de la valeur du VIX
VIX_VALUE=$(echo "$PAGE_CONTENT" | sed -n 's/.*VIX INDEX \([0-9 ]\{1,\},[0-9]\{2\}\).*/\1/p' | tr ',' '.')

# Vérifier si une valeur a été trouvée
if [[ -n "$VIX_VALUE" ]]; then
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$TIMESTAMP,$VIX_VALUE" >> "$OUTPUT"
    echo "[$TIMESTAMP] VIX: $VIX_VALUE enregistré." >> "$LOG_FILE"
else
    echo "[$(date)] Erreur : Impossible d'extraire la valeur du VIX." >> "$LOG_FILE"
fi

# Génération du rapport journalier à 20h
HOUR=$(date '+%H')
if [ "$HOUR" -eq 20 ]; then
    echo "[$(date)] Génération du rapport journalier" >> "$LOG_FILE"

    LAST_24H=$(tail -288 "$OUTPUT")  # 288 points = 5 min * 12h

    OPEN=$(echo "$LAST_24H" | head -1 | cut -d',' -f2)
    CLOSE=$(echo "$LAST_24H" | tail -1 | cut -d',' -f2)

    EVOLUTION=$(awk "BEGIN {print (($CLOSE - $OPEN) / $OPEN) * 100}")

    VOLATILITY=$(echo "$LAST_24H" | cut -d',' -f2 | awk '{sum+=$1; sumsq+=$1*$1} END {print sqrt(sumsq/NR - (sum/NR)^2)}')

    echo "Date: $(date '+%Y-%m-%d')" > "$REPORT_FILE"
    echo "Open Price: $OPEN" >> "$REPORT_FILE"
    echo "Close Price: $CLOSE" >> "$REPORT_FILE"
    echo "Change: $EVOLUTION%" >> "$REPORT_FILE"
    echo "Volatility: $VOLATILITY" >> "$REPORT_FILE"

    echo "[$(date)] Rapport généré avec succès" >> "$LOG_FILE"
fi
