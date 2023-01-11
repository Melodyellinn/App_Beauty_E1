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
  with st.container():
    col3, col4 = st.columns(2)
    col3.subheader("World Map mean pageviews by country")
    df_pie_us_vs_all = data.copy()[data['country']!="(not set)"]
    df_pie_us_vs_all['country'] = df_pie_us_vs_all["country"].apply(lambda x: "United States" if x == "United States" else "other")
    df_pie_undifined_country = data.copy()
    df_pie_undifined_country['country'] = df_pie_undifined_country["country"].apply(lambda x: "Non-définie" if x == "(not set)" else "Définie")
    list_of_country = [[37.09024,-95.712891,"United States"],
                    [20.593684,78.96288,"India"],
                    [46.227638,2.213749,"France"],
                    [35.86166,104.195397,"China"],
                    [61.52401,105.318756,"Russia"],
                    [51.165691,10.451526,"Germany"],
                    [61.92411,25.748151,"Finland"],
                    [55.378051,3.435973,"United Kingdom"],
                    [52.132633,5.291266,"Netherlands"],
                    [56.130366,106.346771,"Canada"]]
    df3 = pd.DataFrame(list_of_country, columns = ["Latitude", 'Longitude', 'country'])
    data_with_coordonate = data.copy().merge(df3,on ="country",how = "left")
    data_for_map = data_with_coordonate[data_with_coordonate['country'] != "(not set)"]
    data_for_map_grouped = data_for_map.groupby("country").agg({"fullVisitorId": ["count","nunique"],
                                    "time_on_site": ["mean","sum","max","min"],
                                    "pageviews": ['mean','sum',"max","min"],
                                    "Latitude": ['first'],
                                    "Longitude": ['first']})
  
    fig_map = px.scatter_mapbox(lat = data_for_map_grouped["Latitude"]['first'],lon = data_for_map_grouped["Longitude"]['first'],size=data_for_map_grouped["time_on_site"]['mean'],color=data_for_map_grouped["pageviews"]['mean'],color_continuous_scale=px.colors.sequential.Viridis,mapbox_style ='open-street-map',size_max=50,zoom=1)
    col3.plotly_chart(fig_map,use_container_width=False)
    col4.subheader("Test")