import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
import glob
from datetime import datetime

DB_ELASTICITA = os.path.join("Elasticita", "Elasticita_recap.db")
DB_AGGREGATI = os.path.join("Aggregati", "Aggregati.db")
DIR_PREVISIONI = os.path.join("Previsioni")

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

def trova_png_piu_recente(simbolo_originale):
    simbolo_png = simbolo_originale.replace(".", "").replace("_", "")
    pattern = os.path.join(DIR_PREVISIONI, f"{simbolo_png}_plot_*.png")
    files = glob.glob(pattern)
    if not files:
        return None, None
    latest_file = max(files, key=os.path.getmtime)
    basename = os.path.basename(latest_file)
    ts = None
    try:
        part = basename.split("_plot_")[1].replace(".png", "")
        ts = datetime.strptime(part, "%Y%m%d_%H%M%S")
    except Exception:
        pass
    return latest_file, ts

st.set_page_config(page_title="Analitico Dati", layout="wide")
st.title("Analitico Dati - Elasticita, Aggregati e Previsioni")

if not os.path.exists(DB_ELASTICITA) or not os.path.exists(DB_AGGREGATI):
    st.error("Database mancanti. Controlla le cartelle 'Elasticita' e 'Aggregati'.")
    st.stop()

recap_df = carica_recap()
simboli = sorted(recap_df["symbol"].dropna().unique())

simbolo_sel = st.selectbox("Seleziona un simbolo:", simboli)

if simbolo_sel:
    st.subheader(f"Dati da Elasticita - {simbolo_sel}")
    recap_row = recap_df[recap_df["symbol"] == simbolo_sel]
    st.dataframe(recap_row, width="stretch")

    st.divider()
    st.subheader("Dati da Aggregati")
    agg_df = carica_tabella_aggregati(simbolo_sel)

    if agg_df.empty:
        st.warning(f"Nessuna tabella trovata per {simbolo_sel.replace('.', '_')}")
    else:
        st.dataframe(agg_df, width="stretch")

        with st.expander("Mostra grafici analitici"):
            num_cols = agg_df.select_dtypes(include='number').columns
            if len(num_cols) > 0:
                x_axis = "periodo" if "periodo" in agg_df.columns else agg_df.index
                for col in num_cols:
                    fig = px.line(agg_df, x=x_axis, y=col, title=f"Andamento di {col}", markers=True)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nessuna colonna numerica trovata per generare grafici.")

    st.divider()
    st.subheader("Previsioni")
    if not os.path.exists(DIR_PREVISIONI):
        st.warning(f"Cartella previsioni non trovata in: {DIR_PREVISIONI}")
    else:
        latest_png, data_png = trova_png_piu_recente(simbolo_sel)
        if latest_png:
            st.image(latest_png, caption=f"Ultima previsione per {simbolo_sel}")
            if data_png:
                st.caption(f"Generata il {data_png.strftime('%d/%m/%Y alle %H:%M:%S')}")
        else:
            st.info("Nessuna previsione disponibile per questo simbolo.")

        if st.button("Aggiorna analisi"):
            st.cache_data.clear()
            try:
                st.rerun()
            except Exception:
                st.experimental_rerun()
