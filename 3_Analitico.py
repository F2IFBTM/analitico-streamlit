import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
import glob
from datetime import datetime

# === Percorsi Database e cartelle ===
DB_ELASTICITA = os.path.join("Elasticita", "Elasticita_recap.db")
DB_AGGREGATI = os.path.join("Aggregati", "Aggregati.db")
DIR_PREVISIONI = os.path.join("Previsioni")

# === Configurazione pagina Streamlit ===
st.set_page_config(
    page_title="Analitico Dati",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CSS personalizzato ===
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #f9fafb 0%, #eef2f7 100%);
    }
    h1 {
        text-align: center;
        color: #0f172a;
        font-weight: 700;
        font-size: 2rem;
        margin-top: 0.5em;
        margin-bottom: 1em;
    }
    h2, h3 {
        color: #1e293b;
        border-left: 5px solid #2563eb;
        padding-left: 10px;
        margin-top: 1em;
    }
    .stDataFrame {
        border-radius: 12px;
        box-shadow: 0px 1px 6px rgba(0,0,0,0.1);
    }
    button {
        border-radius: 10px !important;
        background-color: #2563eb !important;
        color: white !important;
        font-weight: 600 !important;
    }
    .stCaption {
        font-size: 0.9em;
        color: #475569;
    }
</style>
""", unsafe_allow_html=True)

# === Funzioni cache ===
@st.cache_data
def carica_recap():
    with sqlite3.connect(DB_ELASTICITA) as conn:
        df = pd.read_sql_query("SELECT * FROM recap_summary;", conn)
    return df

@st.cache_data
def carica_tabella_aggregati(simbolo):
    tab_name = simbolo.replace(".", "_")
    with sqlite3.connect(DB_AGGREGATI) as conn:
        try:
            df = pd.read_sql_query(f"SELECT * FROM '{tab_name}';", conn)
        except Exception:
            df = pd.DataFrame()
    return df

# === Trova PNG più recente ===
def trova_png_piu_recente(simbolo_originale):
    simboli_possibili = [
        simbolo_originale,
        simbolo_originale.replace(".", ""),
        simbolo_originale.replace(".", "_"),
        simbolo_originale.replace("_", ""),
        simbolo_originale.replace("_", "."),
    ]
    files_trovati = []
    for simb in simboli_possibili:
        pattern = os.path.join(DIR_PREVISIONI, f"{simb}_plot_*.png")
        trovati = glob.glob(pattern)
        if trovati:
            files_trovati.extend(trovati)
    if not files_trovati:
        return None, None
    latest_file = max(files_trovati, key=os.path.getmtime)
    basename = os.path.basename(latest_file)
    ts = None
    try:
        part = basename.split("_plot_")[1].replace(".png", "")
        ts = datetime.strptime(part, "%Y%m%d_%H%M%S")
    except Exception:
        pass
    return latest_file, ts

# === Controllo database ===
if not os.path.exists(DB_ELASTICITA) or not os.path.exists(DB_AGGREGATI):
    st.error("Database mancanti. Controlla le cartelle 'Elasticita' e 'Aggregati'.")
    st.stop()

# === Caricamento recap ===
recap_df = carica_recap()
simboli = sorted(recap_df["symbol"].dropna().unique())

# === Titolo ===
st.title("📊 Analitico Dati — Elasticità, Aggregati e Previsioni")

# === KPI iniziali ===
col1, col2, col3 = st.columns(3)
col1.metric("Simboli analizzati", len(simboli))
col2.metric("Righe Elasticità", len(recap_df))
ultima_data = recap_df["date"].max() if "date" in recap_df.columns else "—"
col3.metric("Ultimo aggiornamento", str(ultima_data))

st.divider()

# === Selettore simbolo ===
simbolo_sel = st.selectbox("🔍 Seleziona un simbolo:", simboli)

if simbolo_sel:
    tab1, tab2, tab3 = st.tabs(["📈 Elasticità", "📊 Aggregati", "🔮 Previsioni"])

    # --- TAB 1: Elasticità ---
    with tab1:
        st.subheader(f"Dati da Elasticità - {simbolo_sel}")
        recap_row = recap_df[recap_df["symbol"] == simbolo_sel]
        st.dataframe(recap_row, use_container_width=True)

        if not recap_row.empty:
            csv = recap_row.to_csv(index=False).encode("utf-8")
            st.download_button("💾 Scarica dati Elasticità (CSV)", csv, f"{simbolo_sel}_elasticita.csv", "text/csv")

    # --- TAB 2: Aggregati ---
    with tab2:
        st.subheader("Dati da Aggregati")
        agg_df = carica_tabella_aggregati(simbolo_sel)
        if agg_df.empty:
            st.warning(f"Nessuna tabella trovata per {simbolo_sel.replace('.', '_')}")
        else:
            st.dataframe(agg_df, use_container_width=True)

            csv_agg = agg_df.to_csv(index=False).encode("utf-8")
            st.download_button("💾 Scarica dati Aggregati (CSV)", csv_agg, f"{simbolo_sel}_aggregati.csv", "text/csv")

            with st.expander("📉 Mostra grafici analitici"):
                num_cols = agg_df.select_dtypes(include='number').columns
                if len(num_cols) > 0:
                    x_axis = "periodo" if "periodo" in agg_df.columns else agg_df.index
                    for col in num_cols:
                        fig = px.line(agg_df, x=x_axis, y=col, title=f"Andamento di {col}", markers=True)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Nessuna colonna numerica trovata per generare grafici.")

    # --- TAB 3: Previsioni ---
    with tab3:
        st.subheader("Previsioni")
        if not os.path.exists(DIR_PREVISIONI):
            st.warning(f"Cartella previsioni non trovata in: {DIR_PREVISIONI}")
        else:
            latest_png, data_png = trova_png_piu_recente(simbolo_sel)
            if latest_png:
                st.image(latest_png, caption=f"Ultima previsione per {simbolo_sel}", use_column_width=True)
                if data_png:
                    st.caption(f"🕒 Generata il {data_png.strftime('%d/%m/%Y alle %H:%M:%S')}")
            else:
                st.info("Nessuna previsione disponibile per questo simbolo.")

        st.divider()
        if st.button("🔄 Aggiorna analisi"):
            st.cache_data.clear()
            try:
                st.rerun()
            except Exception:
                st.experimental_rerun()

