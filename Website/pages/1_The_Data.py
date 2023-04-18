import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import time
from PIL import Image
import calendar
from datetime import datetime, timezone

# Page Config
st.set_page_config(page_title ="Real-Time Electric Load Forecasting",
                    layout="wide",
                    initial_sidebar_state="collapsed",
                    page_icon="⚡")

# Banner Image
image = Image.open('./photos/home_page.png')
st.image(image, use_column_width = 'always')

# Title
st.title('The Data')
st.write(
    '''
    _In order to predict electric load, we need to understand electricity consumption behaviors and how weather & solar conditions impact demand.
    This page allows you to explore 2022 data that was used for our model._
    '''
)

# Load Data
@st.cache_data
def load_data(filename):
    data = pd.read_csv(filename)
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])
    data['day of week'] = data['Timestamp'].dt.dayofweek
    return data 

df = load_data('./pages/data.csv') # col = Timestamp, Load, DNI, HourlyDryBulbTemperature


# Electricity Patterns
st.subheader('Electric Load Usage Behavior')
st.write('Electric load consumption shows heavy seasonality trends that tend to remain stable year over year.')

# Weekly Patterns
weekly_load = df.groupby(['day of week', 'hour', 'minute'])['Load'].mean().reset_index()

for i in range(0,7):
    weekly_load['day of week'].loc[weekly_load['day of week'] == i] = f'010{i+2}2023'
weekly_load['updated_timestamp'] = pd.to_datetime(weekly_load['day of week'].astype(str) + ' ' + weekly_load['hour'].astype(str).str.zfill(2) + weekly_load['minute'].astype(str).str.zfill(2) + '00', 
                                                  format = '%m%d%Y %H%M%S').dt.tz_localize('Etc/GMT+9')

st.markdown('<p style="font-size: 20px;"><b>NYC Average Weekly Load | 2022<b></p>', unsafe_allow_html=True)
a = (alt.Chart(weekly_load)
    .mark_line()
    .encode(
        alt.X('updated_timestamp', title = '', axis = alt.Axis(format = "%a %H:%M")),
        alt.Y('Load', title = 'Avg Load [MWh]'),
    )
)
hover = alt.selection_single(
    fields=['updated_timestamp'],
    nearest=True,
    on="mouseover",
    empty="none",
)
tooltips = (
    alt.Chart(weekly_load)
    .mark_rule()
    .encode(
        x = 'updated_timestamp',
        y = 'Load',
        opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
        tooltip=[
            alt.Tooltip('updated_timestamp:T', title = 'Time', format = "%a %H:%M"),
            alt.Tooltip('Load', title = 'Avg Load [MWh]'),
        ],
    )
    .add_selection(hover)
)
st.altair_chart((a + tooltips).interactive(), use_container_width=True)

st.write(
    '''
    - In a regular week, we can see that electric load is higher during weekdays. This correlates to when offices are open and we need electricity to power corporate buildlings. 
    We also see drops in load during holidays when fewer individuals head into work (not shown in chart above).
    - Daily load spikes during morning pick-up (6:30AM), hitting its peak at 6PM and begins declining as consumers sleep.
    '''
)

# Monthly Load
monthly_load = df.groupby(df['month']).mean().reset_index()
monthly_load['Month'] = monthly_load['month'].astype('int').apply(lambda x: calendar.month_abbr[x])

st.markdown('<p style="font-size: 20px;"><b>NYC Average Monthly Load vs. Temperature | 2022<b></p>', unsafe_allow_html=True)
a = (alt.Chart(monthly_load)
    .mark_line(point = True)
    .encode(
        alt.X('Month:O', title = '', sort= ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
        alt.Y('Load', title = 'Avg Load [MWh]'),
    )
)
b = (alt.Chart(monthly_load)
    .mark_line(point = True)
    .encode(
        alt.X('Month:O', title = '', sort= ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
        alt.Y('HourlyDryBulbTemperature', title = 'Avg Temperature [°F]'),
        color = alt.value("#FFAA00")
    )
)
c = alt.layer(a, b).resolve_scale(y='independent')
st.altair_chart(c, use_container_width=True)

st.write(
    '''
    - Load is highest during summers (Jun - Sep), which happens to be the hottest months and A/C units are running. 
    There is a secondary subpeak that occurs during winter (Dec - Feb) when temperatures are coldest and heating units are being used. 
    Spring and fall typically have the lowest monthly average loads.
    '''
)


# Impact of Weather
st.subheader('Weather Impacts on Electric Load')
st.write(
    '''
    In addition to understanding general load behavior, we know that weather conditions greatly affect electric demand.
    Extreme temperatures, like heat waves and cold snaps, encourages individuals to use more load to power A/C and heating units. Therefore, it is incredibly important for days with extreme weather that we generate enough load.
    Days with higher solar irradiance also corresponds with less load, as consumers can use behind-the-meter solar devices to offset electric load consumption. Therefore, we need less load on those days.
    '''
)

# Show Specific Weather Examples
st.markdown('<p style="font-size: 20px;"><b>Explore specific examples<b></p>', unsafe_allow_html=True)

chosen = st.radio('Explore Different Weather Conditions',
                  options = ('Cold Snap ❄️', 'Heat Wave 🔥', 'Sunny Day ☀️ vs Cloudy Day ☁️'),
                  horizontal = True,
                  label_visibility = 'collapsed'
)

if chosen == 'Cold Snap ❄️':
    cold_snap = df.loc[(df['month'] == 12) & (df['day'] >= 18)]
    cold_snap['cold_snap'] = 'No'
    cold_snap['cold_snap'].loc[(cold_snap['day'] >= 23) & (cold_snap['day'] <= 26)] = 'Yes'

    st.markdown('<p style="font-size: 18px;"><b>Cold Snap ❄️ | Dec 2022<b></p>', unsafe_allow_html=True)
    cold = (alt.Chart(cold_snap)
        .mark_line()
        .encode(
            alt.X('Timestamp', title = '', axis = alt.Axis(format = "%m/%d/%Y")),
            alt.Y('Load', title = 'Load [MWh]', scale = alt.Scale(domain = [4000, 7000])),
            color = alt.Color('cold_snap:O', title = 'Cold Snap', legend = None, scale = alt.Scale(domain = ['No', 'Yes'], range = ['#ADD8E6', '#00008B']))
        )
    )
    cold_temp = (alt.Chart(cold_snap)
        .mark_line(strokeDash=[5, 5])
        .encode(
            alt.X('Timestamp', title = '', axis = alt.Axis(format = "%m/%d/%Y")),
            alt.Y('HourlyDryBulbTemperature', title = 'Temperature [°F]', scale = alt.Scale(domain = [0, 55])),
            color = alt.value("#E32428")
        
        )
    )
    c1 = alt.layer(cold, cold_temp).resolve_scale(y='independent')   
    st.altair_chart((c1), use_container_width=True)
    st.write(
        '''
        - A winter storm hit NY from December 23 to 26, 2022 where blizzards, high winds, snowfall and record cold temperatures hit the US.
        During this time frame, electric load was slightly higher on the coldest day, but in general, it does not differ too much from our baseline.
        '''
    )

if chosen == 'Heat Wave 🔥':
    heat_wave = df.loc[(df['month'] == 7) & (df['day'] >= 13)]
    heat_wave['heat_flag'] = 'No'
    heat_wave['heat_flag'].loc[(heat_wave['day'] >= 19) & (heat_wave['day'] <= 25)] = 'Yes'

    st.markdown('<p style="font-size: 18px;"><b>Heat Wave 🔥 | July 2022<b></p>', unsafe_allow_html=True)
    heat = (alt.Chart(heat_wave)
        .mark_line()
        .encode(
            alt.X('Timestamp', title = '', axis = alt.Axis(format = "%m/%d/%Y")),
            alt.Y('Load', title = 'Load [MWh]', scale = alt.Scale(domain = [5000, 10000])),
            color = alt.Color('heat_flag:O', title = 'Heat Wave', legend = None, scale = alt.Scale(domain = ['No', 'Yes'], range = ['#ADD8E6', '#00008B']))
        )
    )
    heat_temp = (alt.Chart(heat_wave)
        .mark_line(strokeDash=[5, 5])
        .encode(
            alt.X('Timestamp', title = '', axis = alt.Axis(format = "%m/%d/%Y")),
            alt.Y('HourlyDryBulbTemperature', title = 'Temperature [°F]', scale = alt.Scale(domain = [65, 100])),
            color = alt.value("#E32428")
        
        )
    )
    h1 = alt.layer(heat, heat_temp).resolve_scale(y='independent')   
    st.altair_chart((h1), use_container_width=True)
    st.write(
        '''
        - New Yorkers experienced a week-long heat wave (meaning three or more consecutive days with temperatures of at least 90°F) between July 19 and July 25. 
        This marks the first time the city has experienced a seven-day heat wave since 2013 and we see higher than usual load, as individuals crank up their A/C.
        '''
    )

if chosen == 'Sunny Day ☀️ vs Cloudy Day ☁️':
    solar_comp1 = df.loc[(df['month'] == 10) & (df['day'] == 16)]
    solar_comp1 = solar_comp1.groupby(['hour']).mean().reset_index()

    solar_comp2 = df.loc[(df['month'] == 10) & (df['day'] == 17)]
    solar_comp2 = solar_comp2.groupby(['hour']).mean().reset_index()

    col1, col2 = st.columns(2, gap = 'large')
    with col1:
        st.markdown('<p style="font-size: 18px;"><b>Sunny Day ☀️ | 10/16/2022<b></p>', unsafe_allow_html=True)
        load1 = (alt.Chart(solar_comp1)
            .mark_line()
            .encode(
                alt.X('hour', title = 'Hour'),
                alt.Y('Load', title = 'Avg Load [MWh]', scale = alt.Scale(domain = [3000, 6000]))
            )
        )
        solar1 = (alt.Chart(solar_comp1)
            .mark_line()
            .encode(
                alt.X('hour', title = 'Hour'),
                alt.Y('DNI', title = 'Solar Irradiance [DNI]', scale = alt.Scale(domain = [0, 1000])),
                color = alt.value("#FFAA00")
            )
        )
        g1 = alt.layer(load1, solar1).resolve_scale(y='independent')    
        st.altair_chart(g1, use_container_width=True)    
    
    with col2:
        st.markdown('<p style="font-size: 18px;"><b>Cloudy Day ☁️ | 10/17/2022<b></p>', unsafe_allow_html=True)
        load2 = (alt.Chart(solar_comp2)
            .mark_line()
            .encode(
                alt.X('hour', title = 'Hour'),
                alt.Y('Load', title = 'Avg Load [MWh]', scale = alt.Scale(domain = [3000, 6000]))
            )
        )
        solar2 = (alt.Chart(solar_comp2)
            .mark_line()
            .encode(
                alt.X('hour', title = 'Hour'),
                alt.Y('DNI', title = 'Solar Irradiance [DNI]', scale = alt.Scale(domain = [0, 1000])),
                color = alt.value("#FFAA00")
            )
        )
        g2 = alt.layer(load2, solar2).resolve_scale(y='independent')    
        st.altair_chart(g2, use_container_width=True)  

    st.write(
        '''
        - Both days have the same temperature (59°F). However, one day is overcast whereas the other is extremely sunny.
        When it is sunny, behind-the-meter solar devices are used and offsets the need for electric load. 
        '''
    )

# Temperature & Solar Impact on Load
st.markdown('<p style="font-size: 20px;"><b><br>Explore temperature & solar impact on average load<b></p>', unsafe_allow_html=True)

# Filters
col1, col2 = st.columns(2, gap = 'large')

with col1:
    st.markdown('<p style="font-size: 16px;">Select temperature range:</p>', unsafe_allow_html=True)
    temp = st.slider('temp', 0, 100, (0, 100), label_visibility = 'collapsed')

with col2:
    st.markdown('<p style="font-size: 16px;">Select max solar irradiance:</p>', unsafe_allow_html=True)
    solar = st.slider('solar', 0, 1000, 500, label_visibility = 'collapsed')

hourly_load = df.groupby(['hour', 'DNI', 'HourlyDryBulbTemperature'])['Load'].mean().reset_index()
hourly_load_temp = hourly_load.loc[(hourly_load['HourlyDryBulbTemperature'] >= temp[0]) & (hourly_load['HourlyDryBulbTemperature'] <= temp[1])]
hourly_load_temp = hourly_load_temp.loc[hourly_load_temp['DNI'] <= solar ]#[(hourly_load_temp['DNI'] >= solar[0]) & (hourly_load_temp['DNI'] <= solar[1])]

scale = alt.Scale(domain = [0, 50, 100],  range = ['lightblue', 'yellow', 'red'], type = 'linear')
chart = alt.Chart(hourly_load_temp).mark_circle().encode(
    alt.X('hour', title = 'Hour'),
    alt.Y('Load', title = 'Avg Load [MWh]'),
    color = alt.Color('HourlyDryBulbTemperature', title = 'Temperature', scale = scale, legend = alt.Legend(title = 'Temperature', orient = 'top')),
    size = alt.Size('DNI', title = 'Solar Irradiance [DNI]', scale = alt.Scale(range=[10, 100]), legend = alt.Legend(title = 'Solar Irradiance', orient = 'top'))
)
st.altair_chart(chart, use_container_width=True)

st.write(
    '''
    - This chart shows that the hottest temperatures correspond with the highest load and room temperature corresponds with the lowest load. Cold temperatures hover somewhere in between.
    - Solar Irradiance typically picks up around 6am when the sun rises and drops off at 7PM when the sun sets. 
    On days where solar irradiance is high and the temperature is in the mid-50's to 60's, load is lower than if the temperature remains stable but solar is low.
    '''
)
