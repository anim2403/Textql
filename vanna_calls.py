import streamlit as st
from vanna.remote import VannaDefault
import tempfile
import os

@st.cache_resource
def setup_vanna(uploaded_file=None):
    vn = VannaDefault(api_key=st.secrets.get("VANNA_API_KEY"), model='chinook')
    
    if uploaded_file is not None:
        # Create a temporary file for the uploaded database
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Connect to the uploaded SQLite database
        vn.connect_to_sqlite(tmp_file_path)
    else:
        # Connect to the default Chinook database
        vn.connect_to_sqlite("https://vanna.ai/Chinook.sqlite")
    
    return vn

def get_vanna_instance():
    # Check if a database file has been uploaded
    uploaded_file = st.session_state.get('uploaded_db_file')
    
    # Setup Vanna with the appropriate database
    return setup_vanna(uploaded_file)

@st.cache_data(show_spinner="Generating sample questions ...")
def generate_questions_cached():
    vn = get_vanna_instance()
    return vn.generate_questions()

@st.cache_data(show_spinner="Generating SQL query ...")
def generate_sql_cached(question: str):
    vn = get_vanna_instance()
    return vn.generate_sql(question=question, allow_llm_to_see_data=True)

@st.cache_data(show_spinner="Checking for valid SQL ...")
def is_sql_valid_cached(sql: str):
    vn = get_vanna_instance()
    return vn.is_sql_valid(sql=sql)

@st.cache_data(show_spinner="Running SQL query ...")
def run_sql_cached(sql: str):
    vn = get_vanna_instance()
    return vn.run_sql(sql=sql)

@st.cache_data(show_spinner="Checking if we should generate a chart ...")
def should_generate_chart_cached(question, sql, df):
    vn = get_vanna_instance()
    return vn.should_generate_chart(df=df)

@st.cache_data(show_spinner="Generating Plotly code ...")
def generate_plotly_code_cached(question, sql, df):
    vn = get_vanna_instance()
    return vn.generate_plotly_code(question=question, sql=sql, df=df)

@st.cache_data(show_spinner="Running Plotly code ...")
def generate_plot_cached(code, df):
    vn = get_vanna_instance()
    return vn.get_plotly_figure(plotly_code=code, df=df)

@st.cache_data(show_spinner="Generating followup questions ...")
def generate_followup_cached(question, sql, df):
    vn = get_vanna_instance()
    return vn.generate_followup_questions(question=question, sql=sql, df=df)

@st.cache_data(show_spinner="Generating summary ...")
def generate_summary_cached(question, df):
    vn = get_vanna_instance()
    return vn.generate_summary(question=question, df=df)