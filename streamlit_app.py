import streamlit as st
from openai import OpenAI
import os

#st.write("DB Username:", st.secrets["db_username"])
#st.write("DB password:", st.secrets["db_password"])
#st.write("My secrets: ", st.secrets["key1"])

#st.write("Has env var been set:", os.environ["db_username"]==st.secrets["db_username"])

lab1_page = st.Page("Lab 1.py", title="Lab 1")
lab2_page = st.Page("Lab 2.py", title="Lab 2")
lab3_page = st.Page("Lab3.py", title="Lab 3")
lab4_page = st.Page("Lab4.py", title="Lab 4")
lab5_page = st.Page("Lab5.py", title="Lab 5")
pg = st.navigation([lab1_page, lab2_page, lab3_page, lab4_page, lab5_page])
st.set_page_config(page_title="Lab manager")
pg.run()

