import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3 as sql

st.set_page_config(layout = "wide")

conn = sql.connect('Application_prod.db')
data = pd.read_sql("""SELECT * 
                      FROM Raw_data""", conn)

st.header("Behavior visitors on Vaccineshoppe website")
st.markdown('##')
st.write("Date range between 1er octobre 2022 and 31 octobre 2022")
st.markdown('##')
page = st.sidebar.selectbox('Select page',
  ['Country data','Other data'])
if page == 'Country data':
    col1,col2 = st.columns(2)
    df_pie_country = data.copy()[data["country"].isin(["United States", "France", "Russia",
                                                   "India", "China", "Germany", "Finland",
                                                        "Canada", "Netherlands", "United Kingdom"])]
    df_pie_country['country'].value_counts(ascending=False)
    fig = px.pie(df_pie_country, values='pageviews', names='country', title='Top 10 Nombre pageviews par pays')
    col1.plotly_chart(fig,use_container_width=False)
    st.markdown('##')
    st.markdown('##')
    df_unique_user_country = data.copy().groupby(['country', 
    'fullVisitorId']).count().reset_index().groupby("country").count().reset_index()[["country","fullVisitorId"]]
    df_unique_user_country = df_unique_user_country.sort_values('fullVisitorId', ascending=False).head(10)
    df_unique_user_country.groupby(['country']).count().reset_index()
    figure = px.pie(df_unique_user_country, values='fullVisitorId', names='country', title='Top 10 des visiteurs uniques par pays')
    col2.plotly_chart(figure,use_container_width=False)
    
else:
  st.write("Hello")