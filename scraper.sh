#!/bin/bash

# URL de la page contenant les données du VIX
URL="https://www.boursorama.com/bourse/indices/cours/1cVIX/"

# Fichier CSV où les données seront enregistrées
OUTPUT="/home/cmlnrnt/scrap_vix/vix_data.csv"

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
