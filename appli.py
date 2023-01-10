import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout = "wide")
data = pd.read_csv("data/bquxjob_4a55ecd5_184c3af4fbe.csv")
st.header("National Statistics")
page = st.sidebar.selectbox('Select page',
  ['Country data','Continent data'])
if page == 'Country data':
  try:
    df_pie_country = data.copy()[data["country"].isin(["United States", "France", "Russia",
                                                        "India", "China", "Germany", "Finland",
                                                        "Canada", "Netherlands", "United Kingdom"])]
    df_pie_country['country'].value_counts(ascending=False)
    fig = px.pie(df_pie_country, values='pageviews', names='country', title='Top 10 Nombre pageviews par pays')
    fig.show()
  except Exception as e : 
    print(e)
else:
  st.write("Hello")