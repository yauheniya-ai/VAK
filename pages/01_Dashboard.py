import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

# Database connection from Streamlit secrets
def get_db_connection():
    try:
        secrets = st.secrets["connections"]["database"]
        return psycopg2.connect(
            dbname=secrets["database"],
            user=secrets["username"],
            password=secrets["password"],
            host=secrets["host"],
            port=secrets.get("port", "5432")  # Default PostgreSQL port
        )
    except KeyError as e:
        st.error(f"Fehlende Datenbankkonfigurationswerte: {e}")
        st.stop()

# Fetch data from vak_results table
def fetch_vak_results():
    try:
        conn = get_db_connection()
        df = pd.read_sql("SELECT * FROM vak_results", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Fehler beim Abrufen der vak_results-Daten: {e}")
        return pd.DataFrame()

# Fetch data from vak_responses table
def fetch_vak_responses():
    try:
        conn = get_db_connection()
        df = pd.read_sql("SELECT * FROM vak_responses", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Fehler beim Abrufen der vak_responses-Daten: {e}")
        return pd.DataFrame()

# Streamlit Dashboard
st.title("VAK Lernstil-Dashboard")

# Fetch both tables data
vak_results_data = fetch_vak_results()
vak_responses_data = fetch_vak_responses()

if not vak_results_data.empty:
    # Bar Plot of Learning Styles
    st.subheader("Lernstil-Verteilung")
    vak_counts = vak_results_data[['visual', 'auditory', 'kinesthetic']].sum()
    vak_df = pd.DataFrame({"Lernstil": ["Visuell", "Auditiv", "Kinästhetisch"], "Anzahl": vak_counts})
    fig1 = px.bar(vak_df, x="Lernstil", y="Anzahl", title="Verteilung der Lernstile", color="Lernstil")
    st.plotly_chart(fig1)

    # Pie Chart of Participants' Results
    st.subheader("Ergebnisse nach Teilnehmer")
    fig2 = px.pie(vak_results_data, names="result", title="Dominanter Lernstil pro Teilnehmer")
    st.plotly_chart(fig2)

    # Display Raw Data from vak_results table
    st.subheader("Gespeicherte Ergebnisse")
    st.dataframe(vak_results_data)
else:
    st.warning("Keine Daten in der vak_results-Tabelle gefunden. Bitte stelle sicher, dass das Quiz ausgefüllt wurde.")

if not vak_responses_data.empty:
    # Display Raw Data from vak_responses table
    st.subheader("Gespeicherte Antworten")
    st.dataframe(vak_responses_data)
else:
    st.warning("Keine Daten in der vak_responses-Tabelle gefunden. Bitte stelle sicher, dass die Antworten gespeichert wurden.")
