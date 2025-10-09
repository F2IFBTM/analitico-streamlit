# Analitico Streamlit - Deploy Ready

Questa cartella contiene una versione pronta per il deploy su Streamlit Cloud.

## Struttura
```
Analitico_Starter/
├── 3_Analitico.py
├── Elasticita/
│   └── Elasticita_recap.db           (da aggiungere)
├── Aggregati/
│   └── Aggregati.db                  (da aggiungere)
├── Previsioni/
│   └── <SIMBOLO>_plot_YYYYMMDD_HHMMSS.png  (da aggiungere)
├── requirements.txt
└── .streamlit/
    └── config.toml
```

## Uso locale
1) Copia i tuoi file:
   - Elasticita/Elasticita_recap.db
   - Aggregati/Aggregati.db
   - PNG dentro Previsioni/
2) Avvia:
   streamlit run 3_Analitico.py

## Deploy su Streamlit Cloud
1) Crea un repository GitHub e carica tutti i file di questa cartella.
2) Vai su https://share.streamlit.io, collega il repo e scegli 3_Analitico.py come entrypoint.
3) Il sito sarà online in pochi minuti.

## Aggiornare i dati (più volte al giorno)
Quando hai nuovi DB o PNG:
    git add Elasticita Aggregati Previsioni
    git commit -m "Aggiornamento dati"
    git push

Streamlit Cloud esegue un redeploy automatico e l'app legge i nuovi file.

## Nomi PNG previsioni
Devono seguire lo schema:
<SIMBOLO_SENZA_PUNTI>_plot_YYYYMMDD_HHMMSS.png
Esempio: BTCUSD_plot_20251008_133759.png
La didascalia sotto l'immagine viene estratta dalla parte YYYYMMDD_HHMMSS.
