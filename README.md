# Natural Language Database Explore

This Streamlit app empowers users to interact with their local databases using natural language or voice search. It seamlessly integrates the following features:

-   **Database Upload:** Effortlessly drop your local database file (supported formats: `.csv`, `.sqlite`, `.xlsx`) onto the app's interface for intuitive data exploration.
-   **Natural Language Querying:** Formulate your data exploration questions in plain English. The app intelligently translates your queries into SQL, enabling you to retrieve relevant information without writing complex code.
-   **Voice Search:** Enjoy the convenience of voice search. Speak your queries naturally, and the app will transcribe and process them for seamless data interaction.
-   **AI-powered Suggestions:** As you type or speak, receive insightful AI suggestions that enhance your query formulation, leading to more accurate data exploration.
-   **Tabular Output:** The app presents the query results in a clear and concise table format, facilitating easy data comprehension and analysis.
-   **Data Visualization:** Gain deeper insights from your data through interactive visualizations. The app generates customizable charts and graphs based on your query, helping you identify trends and patterns.




# Install

```bash
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
