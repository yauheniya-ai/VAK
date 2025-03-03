import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

# Custom colors for each learning style
custom_colors = {
    "Visuell": "#5C16C1",   # Purple/Violet
    "Auditiv": "#C7BFE3",   # Lavender
    "Kinästhetisch": "#94E047"  # Lime
}

# Mapping old English labels to German
style_mapping = {
    "Visual": "Visuell",
    "Auditory": "Auditiv",
    "Kinesthetic": "Kinästhetisch"
}

# Database connection from Streamlit secrets
def get_db_connection():
    try:
        secrets = st.secrets["connections"]["database"]
        return psycopg2.connect(
            dbname=secrets["database"],
            user=secrets["username"],
            password=secrets["password"],
            host=secrets["host"],
            port=secrets.get("port", "5432") 
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

# Streamlit Page Config
st.set_page_config(
    page_title="VAK Lernstil-Dashboard",
    page_icon="assets/logo_2.png"
)

st.logo("assets/logo_2.png")
st.sidebar.image("assets/Visuell.gif")

# Streamlit Dashboard
st.title("VAK Lernstil-Dashboard")

# Fetch both tables data
vak_results_data = fetch_vak_results()
vak_responses_data = fetch_vak_responses()

if not vak_results_data.empty:
    # Get total number of participants
    total_participants = len(vak_results_data)

    # Bar Plot of Learning Styles
    st.subheader(f"Lernstil-Präferenzen basierend auf allen Antworten")
    vak_counts = vak_results_data[['visual', 'auditory', 'kinesthetic']].sum()
    vak_df = pd.DataFrame({"Lernstil": ["Visuell", "Auditiv", "Kinästhetisch"], "Anzahl": vak_counts})
    
    fig1 = px.bar(
        vak_df, 
        x="Lernstil", 
        y="Anzahl", 
        title=f"Lernstil-Präferenzen unter {total_participants} Teilnehmern", 
        color="Lernstil", 
        text="Anzahl", 
        color_discrete_map=custom_colors
    )
    
    # Vergrößere die Schriftgrößen für Säulenbeschriftungen
    fig1.update_traces(textposition="outside", textfont_size=20)
    fig1.update_layout(
        showlegend=False, 
        xaxis_title="", 
        yaxis_title="Anzahl",
        font=dict(size=20)  # Größere Schriftgröße für Achsen & Labels
    )

    st.plotly_chart(fig1)

    # --- Fix Old English Categories in the Donut Chart ---
    vak_results_data["result"] = vak_results_data["result"].replace(style_mapping)

    # Donut Chart of Participants' Results
    st.subheader("Verteilung der dominanten Lernstile unter den Teilnehmern")
    fig2 = px.pie(
        vak_results_data, 
        names="result", 
        title="Verteilung der dominanten Lernstile", 
        color="result", 
        hole=0.5,  # Converts pie chart into a donut chart
        color_discrete_map=custom_colors
    )

    # Vergrößere Prozentzahlen und Legende
    fig2.update_traces(
        textposition="outside", 
        textinfo="percent+label",
        textfont_size=20
    )

    # Vergrößere Legenden-Schriftgröße
    fig2.update_layout(
        showlegend=False, 
        annotations=[dict(
            text=f"Teilnehmer<br>{total_participants}", 
            x=0.5, y=0.5, 
            font_size=20, 
            showarrow=False
        )]
    )

    st.plotly_chart(fig2)