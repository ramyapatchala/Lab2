import streamlit as st
from openai import OpenAI
import os

#st.write("DB Username:", st.secrets["db_username"])
#st.write("DB password:", st.secrets["db_password"])
#st.write("My secrets: ", st.secrets["key1"])

#st.write("Has env var been set:", os.environ["db_username"]==st.secrets["db_username"])

lab1_page = st.Page("Lab 1.py", title="Lab 1")
lab2_page = st.Page("Lab 2.py", title="Lab 2")
pg = st.navigation([lab1_page, lab2_page])
st.set_page_config(page_title="Lab manager")
pg.run()

