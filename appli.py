import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3 as sql
from datetime import timedelta, datetime
import plotly.graph_objects as go

st.set_page_config(layout = "wide")

## Import Data ##
conn = sql.connect('Application_prod.db')
data = pd.read_sql("""SELECT * 
                      FROM Raw_data""", conn)
df_kpi = pd.read_csv('data/data_app.csv')

## Header ##
st.title("Behavior visitors on Vaccineshoppe website")
st.markdown("<style>h1{text-align: center;}</style>", unsafe_allow_html=True)
st.write("Date range between 1er octobre 2022 and 31 octobre 2022")

## SelectBOX ##
page = st.sidebar.selectbox('Select page',
  ['Country data','Other data'])

## FIRST PAGE ##
if page == 'Country data':
    col1, col2 = st.columns([6, 2], column_width=1)
       
    col1.subheader("Top predict by week")
    top_predict_by_week = df_kpi.copy()
    top_predict_by_week["date"] = pd.to_datetime(top_predict_by_week["date"])
    top_predict_by_week = top_predict_by_week[['date', 'Predict']]
    date1 = "20220917"
    today_date = datetime.strptime(date1,"%Y%m%d")
    last_date = today_date - timedelta(days=7)
    top_predict_this_week = top_predict_by_week.copy()[top_predict_by_week['date'].between(last_date,today_date)]
    date2 = "20220909"
    today_date = datetime.strptime(date2,"%Y%m%d")
    last_date = today_date - timedelta(days=7)
    top_predict_last_week = top_predict_by_week.copy()[top_predict_by_week['date'].between(last_date,today_date)]
    count_predict_this_week = top_predict_this_week.count()[0]
    count_predict_last_week = top_predict_last_week.count()[0]

    fig_kpi = go.Figure()
    fig_kpi.add_trace(go.Indicator(mode = "number+delta",
                                   value = count_predict_this_week,
                                   domain = {'x': [0, 0], 'y': [0, 0]},
                                   delta = {'reference': count_predict_last_week,
                                            'relative': True,
                                            'position' : "bottom",'valueformat':'.2%'}))
    col1.plotly_chart(fig_kpi,use_container_width=False)
    
        
    col2.subheader("Top predict by week")
    top_predict_by_week = df_kpi.copy()
    top_predict_by_week["date"] = pd.to_datetime(top_predict_by_week["date"])
    top_predict_by_week = top_predict_by_week[['date', 'Predict']]
    date1 = "20220917"
    today_date = datetime.strptime(date1,"%Y%m%d")
    last_date = today_date - timedelta(days=7)
    top_predict_this_week = top_predict_by_week.copy()[top_predict_by_week['date'].between(last_date,today_date)]
    date2 = "20220909"
    today_date = datetime.strptime(date2,"%Y%m%d")
    last_date = today_date - timedelta(days=7)
    top_predict_last_week = top_predict_by_week.copy()[top_predict_by_week['date'].between(last_date,today_date)]
    count_predict_this_week = top_predict_this_week.count()[0]
    count_predict_last_week = top_predict_last_week.count()[0]

    fig_kpi = go.Figure()
    fig_kpi.add_trace(go.Indicator(mode = "number+delta",
                                   value = count_predict_this_week,
                                   domain = {'x': [0, 0], 'y': [0, 0]},
                                   delta = {'reference': count_predict_last_week,
                                            'relative': True,
                                            'position' : "bottom",'valueformat':'.2%'}))
    col2.plotly_chart(fig_kpi,use_container_width=False)
  
  ## MAPPING ##  
    col1.subheader("World Map mean pageviews by country")
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
    col1.plotly_chart(fig_map,use_container_width=False)

    
# Create checkboxes to toggle the plots visibility
    show_plot1 = st.checkbox("Show : Top 10 des pageviews par Pays")
    show_plot2 = st.checkbox("Show Top 10 des visiteurs uniques par Pays")
    if show_plot1:
      df_pie_country = data.copy()[data["country"].isin(["United States", "France", "Russia",
                                                   "India", "China", "Germany", "Finland",
                                                        "Canada", "Netherlands", "United Kingdom"])]
      df_pie_country['country'].value_counts(ascending=False)
      fig = px.pie(df_pie_country, values='pageviews', names='country', title='Top 10 Nombre pageviews par pays')
      col1.plotly_chart(fig,use_container_width=False)
    else:
      st.empty()
    
    if show_plot2:
      df_unique_user_country = data.copy().groupby(['country', 
      'fullVisitorId']).count().reset_index().groupby("country").count().reset_index()[["country","fullVisitorId"]]
      df_unique_user_country = df_unique_user_country.sort_values('fullVisitorId', ascending=False).head(10)
      df_unique_user_country.groupby(['country']).count().reset_index()
      figure = px.pie(df_unique_user_country, values='fullVisitorId', names='country', title='Top 10 des visiteurs uniques par pays')
      col1.plotly_chart(figure,use_container_width=False)
    else:
      st.empty()









## SECOND PAGE ##    
else:
  with st.container():
    col4, col5 = st.columns([4, 2])
    col4.subheader("World Map mean pageviews by country")
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
    col4.plotly_chart(fig_map,use_container_width=False)
    
    col5.subheader("Top predict by week")
    top_predict_by_week = df_kpi.copy()
    top_predict_by_week["date"] = pd.to_datetime(top_predict_by_week["date"])
    top_predict_by_week = top_predict_by_week[['date', 'Predict']]
    date1 = "20220917"
    today_date = datetime.strptime(date1,"%Y%m%d")
    last_date = today_date - timedelta(days=7)
    top_predict_this_week = top_predict_by_week.copy()[top_predict_by_week['date'].between(last_date,today_date)]
    date2 = "20220909"
    today_date = datetime.strptime(date2,"%Y%m%d")
    last_date = today_date - timedelta(days=7)
    top_predict_last_week = top_predict_by_week.copy()[top_predict_by_week['date'].between(last_date,today_date)]
    count_predict_this_week = top_predict_this_week.count()[0]
    count_predict_last_week = top_predict_last_week.count()[0]

    fig_kpi = go.Figure()
    fig_kpi.add_trace(go.Indicator(mode = "number+delta",
                                   value = count_predict_this_week,
                                   domain = {'x': [0, 0], 'y': [0, 0]},
                                   delta = {'reference': count_predict_last_week,
                                            'relative': True,
                                            'position' : "bottom",'valueformat':'.2%'}))
    col5.plotly_chart(fig_kpi,use_container_width=False)