#!/bin/bash

# URL de la page contenant les données du VIX
URL="https://www.boursorama.com/bourse/indices/cours/1cVIX/"

# Fichier CSV où les données seront enregistrées
OUTPUT="/scrap_vix/vix_data.csv"

# Récupération de la page HTML
PAGE_CONTENT=$(curl -s "$URL")

# Extraction de la valeur du VIX en remplaçant la virgule par un point
VIX_VALUE=$(echo "$PAGE_CONTENT" | sed -n 's/.*VIX INDEX \([0-9 ]\{1,\},[0-9]\{2\}\).*/\1/p' | tr ',' '.')

# Vérifier si une valeur a été trouvée
if [[ -n "$VIX_VALUE" ]]; then
    # Formatage de l'horodatage (date et heure actuelle)
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

    # Enregistrement de la donnée dans le fichier CSV
    echo "$TIMESTAMP,$VIX_VALUE" >> "$OUTPUT"
    
    # Affichage dans le terminal (optionnel)
    echo "[$TIMESTAMP] VIX: $VIX_VALUE enregistré."
else
    echo "Erreur : Impossible d'extraire la valeur du VIX."
fi
# Fichier du rapport
REPORT_FILE="/home/cmlnrnt/scrap_vix/daily_report.txt"

# Génération du rapport à 20h chaque jour
HOUR=$(date '+%H')
if [ "$HOUR" -eq 20 ]; then
    # Charger les 24 dernières heures de données
    LAST_24H=$(tail -288 vix_data.csv)  # 288 points = 5 min x 12h
    
    # Calcul du prix d'ouverture et de clôture
    OPEN=$(echo "$LAST_24H" | head -1 | cut -d',' -f2)
    CLOSE=$(echo "$LAST_24H" | tail -1 | cut -d',' -f2)
    
    # Calcul de l'évolution en %
    EVOLUTION=$(awk "BEGIN {print (($CLOSE - $OPEN) / $OPEN) * 100}")

    # Calcul de la volatilité (écart-type)
    VOLATILITY=$(echo "$LAST_24H" | cut -d',' -f2 | awk '{sum+=$1; sumsq+=$1*$1} END {print sqrt(sumsq/NR - (sum/NR)**2)}')

    # Écriture du rapport
    echo "Date: $(date '+%Y-%m-%d')" > "$REPORT_FILE"
    echo "Open Price: $OPEN" >> "$REPORT_FILE"
    echo "Close Price: $CLOSE" >> "$REPORT_FILE"
    echo "Change: $EVOLUTION%" >> "$REPORT_FILE"
    echo "Volatility: $VOLATILITY" >> "$REPORT_FILE"
fi
