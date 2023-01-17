#### LIBRARIES ####
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3 as sql
from datetime import timedelta, datetime
## Plotly ##
import ipywidgets
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

#### Import Data ####
conn = sql.connect('Application_prod.db')
data = pd.read_sql("""SELECT * 
                      FROM Raw_data""", conn)

df_kpi = pd.read_csv('data/data_app.csv')

#### DATA FOR KPI ####
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

#### DATA FOR MAP ####
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
#### DATA FOR PIECHART ####

# df_pie_us_vs_all = data.copy()[data['country']!="(not set)"]
# df_pie_us_vs_all['country'] = df_pie_us_vs_all["country"].apply(lambda x: "United States" if x == "United States" else "other")
# df_pie_undifined_country = data.copy()
# df_pie_undifined_country['country'] = df_pie_undifined_country["country"].apply(lambda x: "Non-définie" if x == "(not set)" else "Définie")

# df_unique_user_country = data.copy().groupby(['country', 
#       'fullVisitorId']).count().reset_index().groupby("country").count().reset_index()[["country","fullVisitorId"]]
# df_unique_user_country = df_unique_user_country.sort_values('fullVisitorId', ascending=False).head(10)
# df_unique_user_country.groupby(['country']).count().reset_index()

df_us_vs_all = data.copy()
df_undifined = data.copy()
df_top_10_country = data.copy()
df_us_vs_all["country"] = df_us_vs_all["country"].apply(lambda x : "United States" if x == "United States" else "Other Country or not defined")
df_us_vs_all = df_us_vs_all.groupby("country").count()['bounces']

df_undifined['country']= df_undifined['country'].apply(lambda x : "No defined" if x == "(not set)" else "Country is defined")
df_undifined = df_undifined.groupby("country").count()['bounces']
df_undifined.rename({"bounces":"Nombre de connection"},inplace=True)

df_top_10_country = df_top_10_country[(df_top_10_country['country'] != "(not set)") & (df_top_10_country['country']!= "United States")]
list_of_top_country = list(df_top_10_country.groupby("country").count().sort_values("bounces",ascending=False).head(10).index)
df_top_10_country = df_top_10_country[df_top_10_country['country'].isin(list_of_top_country)]
df_top_10_country = df_top_10_country.groupby("country").count()['bounces']

############################### END DATA ###############################

############################ DEFINE ALL PLOT ############################
#### KPI ####
fig_kpi = go.Figure()
fig_kpi.add_trace(go.Indicator(mode = "number+delta",
                                   value = count_predict_this_week,
                                   domain = {'x': [0, 0], 'y': [0, 0]},
                                   delta = {'reference': count_predict_last_week,
                                            'relative': True,
                                            'position' : "bottom",'valueformat':'.2%'}))
#### MAP ####
fig_map = px.scatter_mapbox(lat = data_for_map_grouped["Latitude"]['first'],
                                lon = data_for_map_grouped["Longitude"]['first'],
                                size=data_for_map_grouped["time_on_site"]['mean'],
                                color=data_for_map_grouped["pageviews"]['mean'],
                                color_continuous_scale=px.colors.sequential.Viridis,
                                mapbox_style ='open-street-map',
                                size_max=50,
                                zoom=1)
#### PIE ####
      # fig = px.pie(df_pie_undifined_country, 
      #              values='pageviews', 
      #              names='country',
      #              title='Top 10 Nombre pageviews par pays',
      #              color_discrete_sequence=px.colors.sequential.Viridis)
      
      # figure = px.pie(df_unique_user_country, 
      #                 values='fullVisitorId', 
      #                 names='country', 
      #                 title='Top 10 des visiteurs uniques par pays',
      #                 color_discrete_sequence= px.colors.sequential.Plasma_r)
      
fig1 = go.Figure(data=[go.Pie(labels=list(df_undifined.index),values=df_undifined.values,hole=0.68,legendgroup=1)])
fig1.update_layout(legend=dict(x=-2,y=0.2))
fig2 =go.Figure(data=[go.Pie(labels=list(df_us_vs_all.index),values=df_us_vs_all.values,hole=0.55,legendgroup=2)])
title_1 = "Nombre d'utilisateur dont le pays n'est pas définie"
title_2 = "Part de la clientèle Américaine"

fig = make_subplots(rows = 1,cols=2,specs=[[{"type":"pie"},{"type":"pie"}]],
                    subplot_titles=[title_1,title_2])
fig.update_layout(showlegend=True,legend = dict(y=0.6),legend_tracegroupgap= 10)

fig.add_trace(fig1['data'][0],row=1,col=1)
fig.add_trace(fig2['data'][0],row=1,col=2)

fig = go.FigureWidget(data=[go.Pie(labels=list(df_top_10_country.index),values=df_top_10_country.values,pull=[0,0,0,0.2])])
fig.update_traces(textposition='inside',hoverinfo='label+value', textinfo='percent+label',showlegend =False,
                  textfont_size=12, marker=dict(line=dict(color='#000000', width=1)))
fig.update_layout(autosize=False,width=800,height=800)


#### PLOT FOR SECOND PAGE ####

rgb_colors = ['rgb(51,138,255)', #hightblue
                  'rgb(14,40,185)',
                  'rgb(23,238,208)', #veryhightblue
                  'rgb(127,228,214)',
                  'rgb(24,189,67)', #green
                  'rgb(57,217,30)',
                  'rgb(19,124,1)',
                  'rgb(12,55,4)']
data_bar = [go.Bar(
            x=data['channelGrouping'].value_counts().index,
            y=data['channelGrouping'].value_counts().values,
            text=data['channelGrouping'].value_counts().values,
            textposition='auto',
            marker=dict(color=rgb_colors)
            )]
layout = go.Layout(title='Countplot of Channels')


second_rgb_colors = ['rgb(255,216,51)',
                  'rgb(255,132,51)',
                  'rgb(248,18,18)']
second_data_bar = [go.Bar(
            x=data['deviceCategory'].value_counts().index,
            y=data['deviceCategory'].value_counts().values,
            text=data['deviceCategory'].value_counts().values,
            textposition='auto',
            marker=dict(color=second_rgb_colors)
            )]
second_layout = go.Layout(title='Countplot of Device Category')

###################################### END CODING ######################################

############################ DASHBOARD APPLICATION STREAMLIT ############################

############## HEADER ##############
st.set_page_config(layout = "wide")
st.title("Behavior visitors on Vaccineshoppe website")
st.markdown("<style>h1{text-align: center;}</style>", unsafe_allow_html=True)
st.write("Date range between 1er octobre 2022 and 31 octobre 2022")

## SelectBOX ##
page = st.sidebar.selectbox('Select page',
  ['Country data','Other data'])

## FIRST PAGE ##
if page == 'Country data':
  row_col01,row_col02,row_col03 = st.columns((.1,3.2,.1))    
  
  with row_col02:
    st.subheader("Count predict by week")
    st.plotly_chart(fig_kpi,use_container_width=False)
    
 ## PLOT MAP ##     
  with row_col02:
    st.subheader("World Map mean pageviews by country")     
    st.plotly_chart(fig_map,use_container_width=True)
    
#### PIE CHART ####
  with row_col02:
    st.plotly_chart(fig1,use_container_width=False)
    st.plotly_chart(fig2,use_container_width=False)

############################ SECONDE PAGE ############################   
else:
  col4, col5 = st.columns([4, 2])
  col4.subheader("Type de channel")

  fig_channel = go.Figure(data=data_bar, layout=layout)
  col4.plotly_chart(fig_channel, use_container_width=False)
    
  col5.subheader("Type of Device")
  fig_device = go.Figure(data=second_data_bar, layout=second_layout)
  col5.plotly_chart(fig_device,use_container_width=False)