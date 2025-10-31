#!/usr/bin/env bash
# ====== TEMPLATE AGGIORNAMENTO DATI ======
# Modifica le variabili sorgente qui sotto
SRC_DB_EL="/path/to/Elasticita_recap.db"
SRC_DB_AG="/path/to/Aggregati.db"
SRC_PNG_DIR="/path/to/Previsioni"

cp -f "$SRC_DB_EL" Elasticita/Elasticita_recap.db
cp -f "$SRC_DB_AG" Aggregati/Aggregati.db
cp -f "$SRC_PNG_DIR"/*.png Previsioni/ 2>/dev/null || true

git add Elasticita Aggregati Previsioni
git commit -m "Aggiornamento dati"
git push
