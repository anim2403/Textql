import time
import streamlit as st
import json
from io import StringIO
import speech_recognition as sr
import pyaudio
from vanna_calls import (
    generate_questions_cached,
    generate_sql_cached,
    run_sql_cached,
    generate_plotly_code_cached,
    generate_plot_cached,
    generate_followup_cached,
    should_generate_chart_cached,
    is_sql_valid_cached,
    generate_summary_cached,
    setup_vanna
)

avatar_url = "https://vanna.ai/img/vanna.svg"

st.set_page_config(layout="wide")

st.sidebar.title("Output Settings")
st.sidebar.checkbox("Show SQL", value=True, key="show_sql")
st.sidebar.checkbox("Show Table", value=True, key="show_table")
st.sidebar.checkbox("Show Plotly Code", value=True, key="show_plotly_code")
st.sidebar.checkbox("Show Chart", value=True, key="show_chart")
st.sidebar.checkbox("Show Summary", value=True, key="show_summary")
st.sidebar.checkbox("Show Follow-up Questions", value=True, key="show_followup")
st.sidebar.button("Reset", on_click=lambda: set_question(None), use_container_width=True)

st.title("TEXTQL")

uploaded_file = st.file_uploader("Upload your SQLite database (optional)", type=["db", "sqlite", "sqlite3"])

if uploaded_file is not None:
    st.session_state['uploaded_db_file'] = uploaded_file
    st.success("Database uploaded successfully. The app will now use your database.")
else:
    st.session_state['uploaded_db_file'] = None
    st.info("Using the default Chinook database. You can upload your own database using the file uploader above.")

# Setup Vanna with the appropriate database
setup_vanna(st.session_state.get('uploaded_db_file'))
def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening... Speak now.")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            st.error("Sorry, I couldn't understand that.")
            return None
        except sr.RequestError:
            st.error("Sorry, there was an error with the speech recognition service.")
            return None
def set_question(question):
    st.session_state["my_question"] = question
if st.button("🎤 Ask with Voice"):
    voice_question = get_voice_input()
    if voice_question:
        st.session_state["my_question"] = voice_question
        st.experimental_rerun()


my_question = st.session_state.get("my_question", default=None)

def set_question(question):
    st.session_state["my_question"] = question

def export_json(df):
    json_string = df.to_json(orient='records')
    json_io = StringIO(json_string)
    return json_io.getvalue()

assistant_message_suggested = st.chat_message("assistant", avatar=avatar_url)
if assistant_message_suggested.button("Click to show suggested questions"):
    st.session_state["my_question"] = None
    questions = generate_questions_cached()
    for i, question in enumerate(questions):
        time.sleep(0.05)
        button = st.button(
            question,
            on_click=set_question,
            args=(question,),
        )

my_question = st.session_state.get("my_question", default=None)

if my_question is None:
    my_question = st.chat_input("Ask me a question about your data")

if my_question:
    st.session_state["my_question"] = my_question
    user_message = st.chat_message("user")
    user_message.write(f"{my_question}")

    sql = generate_sql_cached(question=my_question)

    if sql:
        if is_sql_valid_cached(sql=sql):
            if st.session_state.get("show_sql", True):
                assistant_message_sql = st.chat_message("assistant", avatar=avatar_url)
                assistant_message_sql.code(sql, language="sql", line_numbers=True)
        else:
            assistant_message = st.chat_message("assistant", avatar=avatar_url)
            assistant_message.write(sql)
            st.stop()

        df = run_sql_cached(sql=sql)

        if df is not None:
            st.session_state["df"] = df

        if st.session_state.get("df") is not None:
            if st.session_state.get("show_table", True):
                df = st.session_state.get("df")
                assistant_message_table = st.chat_message("assistant", avatar=avatar_url)
                if len(df) > 10:
                    assistant_message_table.text("First 10 rows of data")
                    assistant_message_table.dataframe(df.head(10))
                else:
                    assistant_message_table.dataframe(df)
                
                # Add export button
                export_button = assistant_message_table.download_button(
                    label="Export as JSON",
                    data=export_json(df),
                    file_name="query_results.json",
                    mime="application/json"
                )

            if should_generate_chart_cached(question=my_question, sql=sql, df=df):
                code = generate_plotly_code_cached(question=my_question, sql=sql, df=df)

                if st.session_state.get("show_plotly_code", False):
                    assistant_message_plotly_code = st.chat_message("assistant", avatar=avatar_url)
                    assistant_message_plotly_code.code(code, language="python", line_numbers=True)

                if code is not None and code != "":
                    if st.session_state.get("show_chart", True):
                        assistant_message_chart = st.chat_message("assistant", avatar=avatar_url)
                        fig = generate_plot_cached(code=code, df=df)
                        if fig is not None:
                            assistant_message_chart.plotly_chart(fig)
                        else:
                            assistant_message_chart.error("I couldn't generate a chart")

            if st.session_state.get("show_summary", True):
                assistant_message_summary = st.chat_message("assistant", avatar=avatar_url)
                summary = generate_summary_cached(question=my_question, df=df)
                if summary is not None:
                    assistant_message_summary.text(summary)

            if st.session_state.get("show_followup", True):
                assistant_message_followup = st.chat_message("assistant", avatar=avatar_url)
                followup_questions = generate_followup_cached(question=my_question, sql=sql, df=df)
                st.session_state["df"] = None

                if len(followup_questions) > 0:
                    assistant_message_followup.text("Here are some possible follow-up questions")
                    # Print the first 5 follow-up questions
                    for question in followup_questions[:5]:
                        assistant_message_followup.button(question, on_click=set_question, args=(question,))

    else:
        assistant_message_error = st.chat_message("assistant", avatar=avatar_url)
        assistant_message_error.error("I wasn't able to generate SQL for that question")
