#### LIBRARIES ####
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3 as sql
from datetime import timedelta, datetime
#### Plotly ####
import ipywidgets
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

#### Import Data ####
conn = sql.connect('Application_prod.db')
data = pd.read_sql("""SELECT * 
                      FROM Raw_data""", conn)
predict_data = pd.read_sql("""SELECT * 
                      FROM Result_data""", conn)

data["id"]= data['index']
predict_data['id'] = predict_data["index"]

d_ = data.set_index("index")
p_ = predict_data.set_index("index")
data_new = d_.merge(p_)
data_new["date"] = pd.to_datetime(data_new["date"])
data_untouch = data_new.copy()

#Fixate date for the last data recieved
start_date_n = data_new.date.max()
end_date_n = start_date_n - timedelta(days=7)
start_date_n1 = end_date_n - timedelta(days=1)
end_date_n1 = start_date_n1 - timedelta(days=7)

#filter
data_new = data_new[data_new["date"].between(end_date_n,start_date_n)]
data_last_week = data_untouch[data_untouch['date'].between(end_date_n1,start_date_n1)]
#df_for_time_yersterday = data_new[data_new["date"].between(end_date_n1,start_date_n1)]



#### END IMPORT & MERGE DATA ####

#### DATA FOR KPI ####
top_predict_by_week = data_new.copy()
#top_predict_by_week["date"] = pd.to_datetime(top_predict_by_week["date"])
top_predict_by_week = top_predict_by_week[['date', 'Predict']]
#date1 = "20220917"
#today_date = datetime.strptime(date1,"%Y%m%d")
#last_date = today_date - timedelta(days=7)
#top_predict_this_week = top_predict_by_week.copy()[top_predict_by_week['date'].between(last_date,today_date)]
#date2 = "20220909"
#today_date = datetime.strptime(date2,"%Y%m%d")
#last_date = today_date - timedelta(days=7)
#top_predict_last_week = top_predict_by_week.copy()[top_predict_by_week['date'].between(last_date,today_date)]
count_predict_this_week = top_predict_by_week.count()[0]
count_predict_last_week = data_last_week.count()[0]


start_date_n = data_new.date.max()
end_date_n = start_date_n - timedelta(days=7)
start_date_n1 = end_date_n - timedelta(days=1)
end_date_n1 = start_date_n1 - timedelta(days=7)
#filter
data_new = data_new[data_new["date"].between(end_date_n,start_date_n)]
data_last_week = data_untouch[data_untouch['date'].between(end_date_n1,start_date_n1)]

percent_of_buyer_this_week = data_new[data_new.Predict == 1].count() / data_new.count()
percent_of_buyer_this_week = np.round(percent_of_buyer_this_week[0],4)*100
percent_of_buyer_last_week = data_last_week[data_last_week.Predict == 1].count() / data_last_week.count()
percent_of_buyer_last_week = np.round(percent_of_buyer_last_week[0],4)*100





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
data_with_coordonate = data_new.copy().merge(df3,on ="country",how = "left")
data_for_map = data_with_coordonate[data_with_coordonate['country'] != "(not set)"]
data_for_map_grouped = data_for_map.groupby("country").agg({"fullVisitorId": ["count","nunique"],
                                    "time_on_site": ["mean","sum","max","min"],
                                    "pageviews": ['mean','sum',"max","min"],
                                    "Latitude": ['first'],
                                    "Longitude": ['first']})

#### DATA FOR PIECHART ####     
df_us_vs_all = data_new.copy()
df_undifined = data_new.copy()
df_top_10_country = data_new.copy()
df_us_vs_all["country"] = df_us_vs_all["country"].apply(lambda x : "United States" if x == "United States" else "Other Country or not defined")
df_us_vs_all = df_us_vs_all.groupby("country").count()['bounces']

df_undifined['country']= df_undifined['country'].apply(lambda x : "No defined" if x == "(not set)" else "Country is defined")
df_undifined = df_undifined.groupby("country").count()['bounces']
df_undifined.rename({"bounces":"Nombre de connections"},inplace=True)

df_top_10_country = df_top_10_country[(df_top_10_country['country'] != "(not set)") & (df_top_10_country['country']!= "United States")]
list_of_top_country = list(df_top_10_country.groupby("country").count().sort_values("bounces",ascending=False).head(10).index)
df_top_10_country = df_top_10_country[df_top_10_country['country'].isin(list_of_top_country)]
df_top_10_country = df_top_10_country.groupby("country").count()['bounces']
## End data for pies ##

### BAR PLOT DATA ###
### BarPlot Channels ###
data_bar_ = data_new.copy()
data_bar_gb = data_bar_.groupby(["channelGrouping","Predict"]).size().reset_index()

data_bar_gb_full = data_bar_gb.groupby("channelGrouping").agg({0:"sum"}).reset_index()

data_bar_join = data_bar_gb.merge(data_bar_gb_full,left_on="channelGrouping",right_on="channelGrouping",
                                  left_index=False,right_index=False,how="left")

data_bar_join['percentage']= data_bar_join['0_x'] / data_bar_join['0_y'] * 100
data_bar_join= data_bar_join.drop("0_y",1)

### BarPlot Device ###
data_bar_2 = data_new.copy()
data_bar_gb2 = data_bar_2.groupby(["deviceCategory","Predict"]).size().reset_index()

data_bar_gb_full2 = data_bar_gb2.groupby("deviceCategory").agg({0:"sum"}).reset_index()

data_bar_join2 = data_bar_gb2.merge(data_bar_gb_full2,left_on="deviceCategory",right_on="deviceCategory",
                                  left_index=False,right_index=False,how="left")

data_bar_join2['percentage']= data_bar_join2['0_x'] / data_bar_join2['0_y'] * 100
data_bar_join2= data_bar_join2.drop("0_y",1)

### DATA FOR TIMELINE ###

df_for_time = data_untouch.copy().groupby("date").agg({"pageviews":"sum",
                                      "time_on_site":"sum",
                                      "medium":"count"})
df_for_time = df_for_time.reset_index()

df_for_time['last_week']= df_for_time['date'].apply(lambda x : "Dernière semaine" if end_date_n <= x <= start_date_n else  "Historique")
minimum_last = df_for_time[df_for_time['last_week']=="Dernière semaine"]["date"].min()
df_two = df_for_time[df_for_time["date"]==minimum_last]
df_two["last_week"]= "Historique"
df_for_time_2 = pd.concat([df_for_time,df_two])

#start_date_n1 = '2022-11-01'
#end_date_n1 = '2022-11-25'

#start_date_n = '2022-11-24'
#end_date_n = '2022-11-31'

#df_for_time_now = df_for_time[df_for_time["date"].between(start_date_n,end_date_n)]
#df_for_time_yersterday = df_for_time[df_for_time["date"].between(start_date_n1,end_date_n1)]


## DECEMBER ##
# df_for_time2 = data_new.groupby("date").agg({"pageviews":"sum",
#                                       "time_on_site":"sum",
#                                       "medium":"count"})
# df_for_time2 = df_for_time2.reset_index()

# start_date_n1_2 = '2022-12-01'
# end_date_n1_2 = '2022-12-25'

# start_date_n_2 = '2022-12-24'
# end_date_n_2 = '2022-12-30'

# df_for_time_now_2 = df_for_time2[df_for_time2["date"].between(start_date_n_2,end_date_n_2)]
# df_for_time_yersterday_2 = df_for_time2[df_for_time2["date"].between(start_date_n1_2,end_date_n1_2)]

############################### END DATA ###############################

############################ DEFINE ALL PLOT ############################

################### KPI PAGE UNE ###################
update_layout01 = go.Layout(
  width=250,
  height=250,
  title = "Premier KPI"
)
kpi_classic = go.Figure(layout= update_layout01)
kpi_classic.add_trace(go.Indicator(mode = "number+delta",
                                   value = count_predict_this_week,
                                   domain = {'x': [0, 0], 'y': [0, 0]},
                                   delta = {'reference': count_predict_last_week,
                                            'relative': True,
                                            'position' : "bottom",'valueformat':'.2%'},
                                   number = {"font":{"size": 50}}))


update_layout02 = go.Layout(
  width=250,
  height=250,
  title = "Second KPI"
)
second_kpi_classic = go.Figure(layout= update_layout02)
second_kpi_classic.add_trace(go.Indicator(mode = "number+delta",
                                   value = percent_of_buyer_this_week,
                                   domain = {'x': [0, 0], 'y': [0, 0]},
                                   delta = {'reference': percent_of_buyer_last_week,
                                            'relative': True,
                                            'position' : "bottom",'valueformat':'.2%'},
                                   number = {"font":{"size": 50},"suffix": "%"}))


update_layout03 = go.Layout(
  width=250,
  height=250,
  title = "Troisième KPI"
)
third_kpi_classic = go.Figure(layout= update_layout03)
third_kpi_classic.add_trace(go.Indicator(mode = "number+delta",
                                   value = count_predict_this_week,
                                   domain = {'x': [0, 0], 'y': [0, 0]},
                                   delta = {'reference': count_predict_last_week,
                                            'relative': True,
                                            'position' : "bottom",'valueformat':'.2%'},
                                   number = {"font":{"size": 50}}))


################### END KPI ###################


################### KPI PAGE TROIS ###################
update_layout = go.Layout(
  width=250,
  height=250,
  title = "Prédictions par semaines (Count)"
)

update_layout2 = go.Layout(
  width=250,
  height=250,
  title = "Second KPI"
)

update_layout3 = go.Layout(
  width=250,
  height=250,
  title = "Troisième KPI"
)



fig_kpi = go.Figure(layout= update_layout)
fig_kpi.add_trace(go.Indicator(mode = "number+delta",
                                   value = count_predict_this_week,
                                   domain = {'x': [0, 0], 'y': [0, 0]},
                                   delta = {'reference': count_predict_last_week,
                                            'relative': True,
                                            'position' : "bottom",'valueformat':'.2%'},
                                   number = {"font":{"size": 50}}))

################### END KPI ###################


#### MAP ####
fig_map = px.scatter_mapbox(lat = data_for_map_grouped["Latitude"]['first'],
                                lon = data_for_map_grouped["Longitude"]['first'],
                                size=data_for_map_grouped["time_on_site"]['mean'],
                                color=data_for_map_grouped["pageviews"]['mean'],
                                color_continuous_scale=px.colors.sequential.Viridis,
                                mapbox_style ='open-street-map',
                                size_max=50,
                                zoom=1)
      
## PIECHART ##      
night_colors = ['rgb(56, 75, 126)', 'rgb(18, 36, 37)']
sun_colors = ['rgb(255,152,2)', 'rgb(254,244,36)']

fig1 = go.Figure(data=[go.Pie(labels=list(df_undifined.index),values=df_undifined.values,hole=0.68,legendgroup=1,
                                marker_colors=night_colors)])
fig1.update_layout(legend=dict(x=-2,y=0.2))
fig2 =go.Figure(data=[go.Pie(labels=list(df_us_vs_all.index),values=df_us_vs_all.values,hole=0.55,legendgroup=2,
                            marker_colors=sun_colors)])
title_1 = "              Nombre d'utilisateurs dont le pays n'est pas défini"
title_2 = "Part de la clientèle Américaine"

double_piechart = make_subplots(rows = 1,cols=2,specs=[[{"type":"pie"},{"type":"pie"}]],
                    subplot_titles=[title_1,title_2])
double_piechart.update_layout(showlegend=True,legend = dict(y=0.6),legend_tracegroupgap= 10)

double_piechart.add_trace(fig1['data'][0],row=1,col=1)
double_piechart.add_trace(fig2['data'][0],row=1,col=2)

## SECOND FIG PIECHART ##
country_colors = ['rgb(157,212,222)', #Canada
                  'rgb(111,168,216)', #China
                  'rgb(46,137,213)', #Finlande
                  'rgb(254,244,36)', # France
                  'rgb(113,209,247)', #Germany
                 'rgb(250,157,22)', # India
                  'rgb(25,84,133)', # Mexico
                 'rgb(75,185,230)', # Netherlands
                  'rgb(10,48,79)', # Philippines
                  'rgb(39,118,184)'] # UK

piechart_country = go.FigureWidget(data=[go.Pie(labels=list(df_top_10_country.index),values=df_top_10_country.values,
                                               pull=[0,0,0,0.1],
                                              marker_colors=country_colors)])

piechart_country.update_traces(textposition='inside',hoverinfo='label+value', textinfo='percent+label',showlegend =False,
                  textfont_size=12, marker=dict(line=dict(color='#000000', width=1)))
piechart_country.update_layout(autosize=False,width=800,height=800,
                             title="Nombre de connections sur le site par Pays")

### Bar plot classic ###
rgb_colors = ['rgb(51,138,255)', #hightblue
                  'rgb(14,40,185)',
                  'rgb(23,238,208)', #veryhightblue
                  'rgb(127,228,214)',
                  'rgb(24,189,67)', #green
                  'rgb(57,217,30)',
                  'rgb(19,124,1)',
                  'rgb(12,55,4)']
data_bar = [go.Bar(
            y=data_new['channelGrouping'].value_counts().values,
            x=data_new['channelGrouping'].value_counts().index,
            text=data_new['channelGrouping'].value_counts().values,
            textposition='auto',
            marker=dict(color=rgb_colors)
            )]
layout = go.Layout(title='Countplot of Channels')


second_rgb_colors = ['rgb(255,216,51)',
                  'rgb(255,132,51)',
                  'rgb(248,18,18)']
second_data_bar = [go.Bar(
            x=data_new['deviceCategory'].value_counts().index,
            y=data_new['deviceCategory'].value_counts().values,
            text=data_new['deviceCategory'].value_counts().values,
            textposition='auto',
            marker=dict(color=second_rgb_colors)
            )]
second_layout = go.Layout(title='Countplot of Device Category')



#### TIMELINE PLOTS ####
## Pageviews ##
time_figure_pageviews = px.line(df_for_time_2, x='date', y='pageviews', 
                                color ="last_week",title='Time Series with Rangeslider')
time_figure_pageviews.update_xaxes(rangeslider_visible=True)
## Time of Site ##
time_figure_timeOnSite = px.line(df_for_time_2, x='date', y='time_on_site',
                                 color ="last_week",title='Time Series with Rangeslider')
time_figure_timeOnSite.update_xaxes(rangeslider_visible=True)


# trace1 = go.Scatter(x=df_for_time_now["date"],y= df_for_time_now['time_on_site'], mode='lines+markers',
#                     name="Donnée de la semaine passée")
# trace2 = go.Scatter(x=df_for_time_yersterday["date"],y= df_for_time_yersterday['time_on_site'],
#                     mode='lines+markers',name = 'Historique du mois')

# fig_1_timeline = go.Figure([trace1,trace2])
# fig_1_timeline.update_layout(title='Temps passé sur le site par jour',
#                    xaxis_title='Date',
#                    yaxis_title='Temps passé sur le site (secondes)')


# trace3 = go.Scatter(x=df_for_time_now["date"],y= df_for_time_now['pageviews'],
#                     mode='lines+markers',name="Donnée de la semaine passée")
# trace4 = go.Scatter(x=df_for_time_yersterday["date"],y= df_for_time_yersterday['pageviews'],
#                     mode='lines+markers',name = 'Historique du mois')

# fig_2_timeline = go.Figure([trace3,trace4])
# fig_2_timeline.update_layout(title='Page visitée sur le site par jour',
#                    xaxis_title='Date',
#                    yaxis_title='Nombre de page vue sur le site')

# ## DECEMBER ##
# trace4 = go.Scatter(x=df_for_time_now_2["date"],y= df_for_time_now_2['time_on_site'], mode='lines+markers',
#                     name="Donnée de la semaine passée")
# trace5 = go.Scatter(x=df_for_time_yersterday_2["date"],y= df_for_time_yersterday_2['time_on_site'],
#                     mode='lines+markers',name = 'Historique du mois')

# fig_3_timeline = go.Figure([trace4,trace5])
# fig_3_timeline.update_layout(title='Temps passé sur le site par jour',
#                    xaxis_title='Date',
#                    yaxis_title='Temps passé sur le site (secondes)')


# trace6 = go.Scatter(x=df_for_time_now_2["date"],y= df_for_time_now_2['pageviews'],
#                     mode='lines+markers',name="Donnée de la semaine passée")
# trace7 = go.Scatter(x=df_for_time_yersterday_2["date"],y= df_for_time_yersterday_2['pageviews'],
#                     mode='lines+markers',name = 'Historique du mois')

# fig_4_timeline = go.Figure([trace6,trace7])
# fig_4_timeline.update_layout(title='Page visitée sur le site par jour',
#                    xaxis_title='Date',
#                    yaxis_title='Nombre de page vue sur le site')

#### DEFINE BAR PLOT PERCENTAGE MODEL PREDICTIONS ####

##CHANNEL##
data_bar_join.columns = ['channelGrouping', 'Predict', 'Counts', 'Percentage']
bar_channel= px.bar(data_bar_join, x='channelGrouping', y=['Percentage'], 
       color='Predict',
       title= "Predictions (Channels)",
       text=data_bar_join['Percentage'].apply(lambda x: '{0:1.2f}%'.format(x)))
##DEVICE##
data_bar_join2.columns = ['deviceCategory', 'Predict', 'Counts', 'Percentage']
bar_device= px.bar(data_bar_join2, x='deviceCategory', y=['Percentage'], 
       color='Predict',
       title= "Predictions (Devices)",
       text=data_bar_join2['Percentage'].apply(lambda x: '{0:1.2f}%'.format(x)))


###################################### END CODING PLOT ######################################


############################ DASHBOARD APPLICATION STREAMLIT ############################

############## HEADER ##############
st.set_page_config(layout = "wide")

##### CSS BALISES #####
## CSS IMG ##
st.markdown(
    """
    <style>
        [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True
)
## CSS TITLE PLOT ##
st.markdown(
    """
    <style>
        [data-testid=stText]{
            font-family: Arial;
            color: green;
            font-size: 20px;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True
)
##### END #####

### TITLE AND LOGO ###
st.image("https://uploads-ssl.webflow.com/5e078c0ced2a27efc66f1263/6081aa3ac9bc20daeef97084_vaccine-shoppe-logo.png")
st.title("Comportement des visiteurs sur Vaccineshoppe.com")
st.markdown("<style>h1{font-family: Georgia; color: rgb(22, 108, 250); font-size: 42px; text-align: center;}</style>",
            unsafe_allow_html=True)
st.write("**Scope date Janvier 2023** :date:")
st.markdown('##')
st.markdown('##')

## SelectBOX ##
page = st.sidebar.selectbox('Select page',
  ['Global','World', 'Prédictions'])

############################ FIRST PAGE ############################
if page == 'Global': 
############ KPI ############    
  row_0_margin_1, row_0_col_1,row_0_margin_2, row_0_col_2,\
  row_0_margin_3, row_0_col_3, row_0_margin_4 = st.columns((.1, 1., 2.5 ,1., 2.5, 1., .1))
  with row_0_col_1:
    st.plotly_chart(kpi_classic ,use_container_width=False)
################### WIP ######################
  with row_0_col_2:
    st.plotly_chart(second_kpi_classic ,use_container_width=False)
  with row_0_col_3:
    st.plotly_chart(third_kpi_classic ,use_container_width=False)

    #### BAR PLOT ####
  row_01_margin_1, row_01_col_1, row_01_margin_2 = st.columns((.1,3.5,.1))
  with row_01_col_1:
    st.text('Count type de channel')
    fig_channel = go.Figure(data=data_bar, layout=layout)
    st.plotly_chart(fig_channel, use_container_width=False)
  row_1_margin_1, row_1_col_1, row_1_margin_2 = st.columns((.1,3.5,.1))  
  with row_1_col_1: 
    st.text("Count type d'appareil")
    fig_device = go.Figure(data=second_data_bar, layout=second_layout)
    st.plotly_chart(fig_device,use_container_width=False)
    
############################ SECONDE PAGE ############################
elif page == 'World':
  ## PLOT MAP ##
  row_2_margin_1,row_2_col_1,row_2_margin_2 = st.columns((.1,7,.1))     
  with row_2_col_1:
    st.text('World Map moyennes des pages visitées par pays')
    st.plotly_chart(fig_map,use_container_width=True)
    
    #### PIE CHART ####
  row_3_margin_1,row_3_col_1,row_3_margin_2 = st.columns((.1,2.5,.1)) 
  with row_3_col_1:
    st.text('Répartitions des Pays')
    st.plotly_chart(double_piechart,use_container_width=True)
    
  row_4_margin_1,row_4_col_1,row_4_margin_2 = st.columns((.5,3.5,.1))
  with row_4_col_1:
    st.plotly_chart(piechart_country,use_container_width=True)
    
############################ THIRD PAGE ############################ 
else:  
############ BARPLOT ############
  row_7_margin_1,row_7_col_1,row_7_margin_2 = st.columns((.1,1.5,.1)) 
  with row_7_col_1:
    st.text('Barplots prédictions des Channels & Appareils')  
  row_8_margin_1,row_8_col_1,row_8_margin_2, row_8_col_2, row_8_margin_3 = st.columns((.1,2.,.1,1.5,.1))  
  with row_8_col_1:
    st.plotly_chart(bar_channel, use_container_width=False)
  with row_8_col_2: 
    st.plotly_chart(bar_device, use_container_width=False)

## Timelines ##
  row_9_margin_1,row_9_col_1,row_9_margin_2 = st.columns((.1,1.5,.1))
  with row_9_col_1:
    st.text('TimeSeries sur les quatre derniers mois (Sept 2022 - Janv 2023)')
  row_10_margin_1,row_10_col_1, row_10_margin_2 = st.columns((.1,2.5,.1)) 
  with row_10_col_1:
    st.plotly_chart(time_figure_pageviews, use_container_width=True)
  row_11_margin_1,row_11_col_1,row_11_margin_2 = st.columns((.1,1.5,.1))
  with row_11_col_1:
    st.plotly_chart(time_figure_timeOnSite, use_container_width=True)
    
    