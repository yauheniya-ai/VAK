import streamlit as st
import psycopg2
import json
import random
import os
import pandas as pd
import plotly.express as px

# Custom colors for each learning style
custom_colors = {
    "Visuell": "#5C16C1",   # Purple/Violet
    "Auditiv": "#C7BFE3",   # Lavender
    "Kinästhetisch": "#94E047"  # Lime
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

# Load Questions from JSON
def load_questions():
    file_path = os.path.join("data", "questions.json")
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# Load the questions
QUESTIONS = load_questions()

# Initialize session state for shuffled options (shuffled only once)
if "shuffled_questions" not in st.session_state:
    st.session_state.shuffled_questions = []
    for q in QUESTIONS:
        shuffled_options = random.sample(q["options"], len(q["options"]))  # Shuffle once
        st.session_state.shuffled_questions.append({"question": q["question"], "options": shuffled_options})


st.set_page_config(
    page_title="VAK Lernstil-Quiz",
    page_icon="assets/logo_1.png"
)

st.logo("assets/logo_1.png")

st.sidebar.image("assets/Kinaesthetisch.gif")

# Streamlit App
st.title("VAK Lernstil-Quiz")
st.image("assets/cover.png", use_container_width=True)
st.write("Beantworte die folgenden Fragen, indem du eine oder mehrere Antworten auswählst. **Jede Frage muss beantwortet werden.**")

# Ask for user's name
name = st.text_input("Bitte gib deinen Namen ein:")

responses = []
user_answers = {}
missing_questions = []  # Track unanswered questions

# Mapping English learning styles to German
style_mapping = {"Visual": "Visuell", "Auditory": "Auditiv", "Kinesthetic": "Kinästhetisch"}

for i, q in enumerate(st.session_state.shuffled_questions):  # Use stored shuffled questions
    st.write(f"{i+1}. {q['question']}")

    selected_options = []  # Store checked answers for this question
    
    for option in q["options"]:
        if st.checkbox(option["text"], key=f"q{i}_{option['text']}"):
            selected_options.append(option["text"])
    
    if selected_options:
        # Store selected answers
        user_answers[q["question"]] = selected_options
        
        # Map selected answers to learning types
        for option in q["options"]:
            if option["text"] in selected_options:
                mapped_type = style_mapping.get(option["type"], option["type"])  # Convert to German
                responses.append(mapped_type)
    else:
        missing_questions.append(i + 1)  # Store missing question number

if st.button("Quiz abschließen"):
    if not name:
        st.warning("⚠️ Bitte gib deinen Namen ein.")
    elif missing_questions:
        missing_str = ", ".join(map(str, missing_questions))
        st.warning(f"⚠️ Bitte beantworte alle Fragen. Du hast die folgenden Fragen übersprungen: **{missing_str}**.")
    else:
        # Initialize counts for each learning style
        counts = {"Visuell": 0, "Auditiv": 0, "Kinästhetisch": 0}
        
        for response in responses:
            if response in counts:  # Ensure valid response before updating
                counts[response] += 1
        
        # Find the highest score
        max_count = max(counts.values())

        # Find all dominant learning styles (handle ties)
        dominant_styles = [style for style, count in counts.items() if count == max_count]

        # Format the result correctly in German
        if len(dominant_styles) == 1:
            result_text = dominant_styles[0]
        elif len(dominant_styles) == 2:
            result_text = f"{dominant_styles[0]}-{dominant_styles[1]}"
        else:
            result_text = f"{dominant_styles[0]}-{dominant_styles[1]}-{dominant_styles[2]}"

        st.success(f"{name}, dein bevorzugter Lernstil ist: **{result_text}**.")

        # Save to database
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Save user responses
            for question, selected in user_answers.items():
                cur.execute(
                    "INSERT INTO vak_responses (name, question, answer) VALUES (%s, %s, %s)",
                    (name, question, ", ".join(selected))
                )
            
            # Save learning style result
            cur.execute(
                "INSERT INTO vak_results (name, visual, auditory, kinesthetic, result) VALUES (%s, %s, %s, %s, %s)",
                (name, counts["Visuell"], counts["Auditiv"], counts["Kinästhetisch"], result_text)
            )
            
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"❌ Fehler beim Speichern: {e}")

# --- Generate Plotly Bar Chart (Säulendiagramm) ---
        vak_df = pd.DataFrame({
            "Lernstil": ["Visuell", "Auditiv", "Kinästhetisch"], 
            "Anzahl": [counts["Visuell"], counts["Auditiv"], counts["Kinästhetisch"]]
        })
        max_value = vak_df["Anzahl"].max()
        y_max = max_value * 1.1
        fig = px.bar(
            vak_df, 
            x="Lernstil", 
            y="Anzahl", 
            title=f"Lernstil-Auswertung für {name}", 
            color="Lernstil",
            text="Anzahl",
            color_discrete_map=custom_colors
        )

        fig.update_traces(textposition="outside")

        fig.update_layout(
            showlegend=False,  
            xaxis_title="",  
            yaxis_title="Anzahl",
            yaxis_range=[0, y_max],
            font=dict(size=20)
        )

        # Show the chart in Streamlit
        st.plotly_chart(fig)

        # Provide a download button for the chart
        st.download_button(
            label="📥 Diagramm herunterladen",
            data=fig.to_image(format="png"),
            file_name=f"Lernstil_Auswertung_{name}.png",
            mime="image/png"
        )

