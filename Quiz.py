import streamlit as st
import psycopg2

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

# VAK Quiz Questions in German
QUESTIONS = [
    {"question": "Wie lernst du am besten?", "options": ["Indem ich Bilder sehe", "Indem ich zuhöre", "Indem ich es selbst mache"]},
    {"question": "Wenn du eine neue Fähigkeit lernst, bevorzugst du…", "options": ["Bilder oder Diagramme", "Erklärungen anhören", "Es ausprobieren"]},
    {"question": "Wenn du eine Wegbeschreibung bekommst, ist es einfacher für dich…", "options": ["Eine Karte zu sehen", "Die Richtung zu hören", "Den Weg selbst zu gehen"]},
    {"question": "Wenn du etwas Neues lernst, was hilft dir mehr?", "options": ["Visuelle Darstellungen", "Gesprochene Anweisungen", "Praktische Erfahrungen"]},
    {"question": "Wie kannst du dir am besten eine Geschichte merken?", "options": ["Indem ich sie sehe", "Indem ich sie höre", "Indem ich sie nachspiele"]},
    {"question": "Was hilft dir, Informationen besser zu behalten?", "options": ["Grafiken und Diagramme", "Audioaufnahmen und Erklärungen", "Selbst ausprobieren und Üben"]},
    {"question": "Wenn du an einen Ort reist, was ist für dich am hilfreichsten?", "options": ["Ein Stadtplan", "Jemand, der dir den Weg beschreibt", "Die Umgebung selbst zu erkunden"]},
    {"question": "Wie gehst du mit neuen Aufgaben um?", "options": ["Ich schaue mir Beispiele an", "Ich frage nach Erklärungen", "Ich versuche, es direkt zu tun"]},
    {"question": "Wenn du versuchst, dich an etwas zu erinnern, wie gehst du vor?", "options": ["Ich visualisiere es", "Ich höre die Information nochmal", "Ich stelle es mir vor und tue es"]},
    {"question": "Welche Methode bevorzugst du beim Erlernen von Sprachen?", "options": ["Bilder und Flashcards", "Hören von Gesprächen", "Sprechen und Üben"]},
    {"question": "Welche Art von Anweisungen bevorzugst du?", "options": ["Visuelle Anleitungen", "Mündliche Erklärungen", "Praktische Übungen"]},
    {"question": "Was hilft dir, dich an den Ablauf eines Ereignisses zu erinnern?", "options": ["Einen Zeitstrahl zu sehen", "Den Ablauf zu hören", "Den Ablauf selbst zu erleben"]},
    {"question": "Wie lernst du am besten komplexe Informationen?", "options": ["Durch Diagramme und Visualisierungen", "Indem ich jemandem zuhöre", "Indem ich es ausprobiere"]},
    {"question": "Wenn du dich auf eine Präsentation vorbereitest, was bevorzugst du?", "options": ["Visuelle Hilfsmittel wie Folien", "Den Vortrag zu hören", "Praktische Übungen"]},
    {"question": "Wie gehst du mit einer neuen Aufgabe um, die du noch nie gemacht hast?", "options": ["Ich schaue mir ein Beispiel an", "Ich lasse mir die Schritte erklären", "Ich probiere es direkt aus"]},
    {"question": "Welche Art von Lernumgebung bevorzugst du?", "options": ["Eine visuelle Umgebung mit vielen Bildern", "Eine ruhige, in der ich zuhören kann", "Eine Umgebung, in der ich aktiv sein kann"]},
    {"question": "Wie behältst du Informationen, die du in einem Meeting gehört hast?", "options": ["Indem ich mir Notizen mache", "Indem ich den Inhalt noch einmal höre", "Indem ich die besprochenen Themen anwende"]},
    {"question": "Was ist für dich der beste Weg, um Anweisungen zu verstehen?", "options": ["Die Anweisungen zu sehen", "Die Anweisungen zu hören", "Die Anweisungen selbst umzusetzen"]},
    {"question": "Wie erinnerst du dich an den Verlauf eines Gesprächs?", "options": ["Durch visuelle Notizen", "Durch das Hören der gesprochenen Worte", "Durch das Nachspielen des Gesprächs"]},
    {"question": "Was ist der effektivste Weg, für dich zu lernen?", "options": ["Indem ich es sehe", "Indem ich es höre", "Indem ich es tue"]},
    {"question": "Wenn du dir etwas merken musst, wie tust du das am liebsten?", "options": ["Indem ich ein Bild vor meinem inneren Auge sehe", "Indem ich es laut wiederhole", "Indem ich es selbst erfahre"]},
]

# Streamlit App
st.title("VAK Lernstil-Quiz")
st.image("assets/cover.png", use_container_width=True)
st.write("Beantworte die folgenden 20 Fragen, um deinen bevorzugten Lernstil zu erfahren.")

# Ask for user's name
name = st.text_input("Bitte gib deinen Namen ein:")
st.write(f"Dein Name: {name}") 

responses = []
for i, q in enumerate(QUESTIONS[:20]):
    st.write(f"{i+1}. {q['question']}")
    choice = st.radio("", q['options'], index=None, key=f"q{i}")
    responses.append(choice)

if st.button("Quiz abschließen"):
    if not name:
        st.warning("Bitte gib deinen Namen ein.")
    elif None in responses:
        st.warning("Bitte wähle eine Antwort für jede Frage.")
    else:
        # Initialize counts for each style
        visual = 0
        auditory = 0
        kinesthetic = 0

        # Count learning styles based on the index of the selected answers
        for i, response in enumerate(responses):
            if i % 3 == 0:  # First option is Visual
                visual += 1
            elif i % 3 == 1:  # Second option is Auditory
                auditory += 1
            elif i % 3 == 2:  # Third option is Kinesthetic
                kinesthetic += 1

        # Determine dominant style
        result = max([(visual, "Visuell"), (auditory, "Auditiv"), (kinesthetic, "Kinästhetisch")], key=lambda x: x[0])
        st.success(f"{name}, dein bevorzugter Lernstil ist: {result[1]}")
        
        # Save to database
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Ensure all responses are inserted into the database
            for i, response in enumerate(responses):
                cur.execute("INSERT INTO vak_responses (name, question, answer) VALUES (%s, %s, %s)",
                            (name, QUESTIONS[i]['question'], response))
            
            # Save the counts for visual, auditory, kinesthetic
            cur.execute("INSERT INTO vak_results (name, visual, auditory, kinesthetic, result) VALUES (%s, %s, %s, %s, %s)",
                        (name, visual, auditory, kinesthetic, result[1]))
            
            conn.commit()
            cur.close()
            conn.close()
            st.write("Ergebnis wurde gespeichert.")
        except Exception as e:
            st.error(f"Fehler beim Speichern: {e}")
