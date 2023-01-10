import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3 as sql

st.set_page_config(layout = "wide")

conn = sql.connect('Application_prod.db')
data = pd.read_sql("""SELECT * 
                      FROM Raw_data""", conn)

st.header("National Statistics")
page = st.sidebar.selectbox('Select page',
  ['Country data','Continent data'])
if page == 'Country data':
    col1,col2 = st.columns(2)
    df_pie_country = data.copy()[data["country"].isin(["United States", "France", "Russia",
                                                   "India", "China", "Germany", "Finland",
                                                        "Canada", "Netherlands", "United Kingdom"])]
    df_pie_country['country'].value_counts(ascending=False)
    fig = px.pie(df_pie_country, values='pageviews', names='country', title='Top 10 Nombre pageviews par pays')
    fig.show()
    col1.plotly_chart(fig,use_container_width=True)
else:
  st.write("Hello")