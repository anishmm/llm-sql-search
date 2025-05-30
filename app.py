import streamlit as st
from langchain.chains import create_sql_query_chain
from langchain_groq import ChatGroq
from sqlalchemy.exc import ProgrammingError
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv() 

db = SQLDatabase.from_uri("sqlite:///Chinook.db")

llm=ChatGroq(model="llama3-70b-8192")


custom_prompt = PromptTemplate.from_template(
    """You are a SQLite expert. Given the input question and database table information, generate an SQL query.

    Input: {input}
    Table Info: {table_info}
    Top K: {top_k}

    If there are any of the above mistakes, rewrite the query.
    If there are no mistakes, just reproduce the original query with no further commentary.

    Output the final SQL query only."""
)

chain = create_sql_query_chain(llm=llm, db=db, prompt=custom_prompt)

def execute_query(question):
    try:
        # Generate SQL query from question
        response = chain.invoke({"question": question, "top_k": 10})
        print(f"response: {response}")

        cleaned_query = response.strip('```sql\n').strip('\n```')
        print(f"cleaned_query: {cleaned_query}")
        # Execute the query
        result = db.run(cleaned_query)
                
        # Return the query and the result
        return response, result
    except ProgrammingError as e:
        st.error(f"An error occurred: {e}")
        return None, None

# Streamlit interface
st.title("SQL Answering App")
st.write("Sample Questions:")
st.markdown("1 show me the total sales by year base.")
st.markdown("2 what is the top selling product in 2012 and 2013?")
st.markdown("3 who is the top customer in 2013?")
st.markdown("4 what was the top selling product in 2011 ?")
st.markdown("5 List the track composed by 'Steven Tyler' ")
st.markdown("6 create a sales summary by country.")
            

# Input from user
question = st.text_input("Enter your question:")

if st.button("Execute"):
    if question:
        cleaned_query, query_result = execute_query(question)
        
        if cleaned_query and query_result is not None:
            st.write("Generated SQL Query:")
            st.code(cleaned_query, language="sql")
            st.write("Query Result:")
            st.write(query_result)
        else:
            st.write("No result returned due to an error.")
    else:
        st.write("Please enter a question.")
        