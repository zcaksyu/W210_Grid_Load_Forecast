import streamlit as st
import pandas as pd
import numpy as np
import time
import os
import altair as alt
from PIL import Image
import base64
from datetime import datetime
from collect_inputs import *
from vega_datasets import data


# Page Config
st.set_page_config(page_title ="Real-Time Electric Load Forecasting",
                    layout="wide",
                    initial_sidebar_state="collapsed",
                    page_icon="⚡")


# Title
col1, col2 = st.columns((3,2))

with col1:
    st.title('Real-Time Electric Load Forecasting ⚡')

with col2: 
    st.write(
    '''
    ##
    Using machine learning to predict real-time electric demand for New York City based on current solar and weather conditions
    '''
    )


# Calculations
st.header('NYC Forecasted Electric Demand')

# Forecast
st.markdown('<p style="font-size: 20px;"><b>Forecasted Load for the Next 90 Minutes<b></p>', unsafe_allow_html=True)
st.markdown(
    '''
    These predictions were calculated using an LSTM model. For more info about our model and inputs, check out our <a href='https://github.com/zcaksyu/W210-Grid-Load-Forecast'>github</a>.
    '''
    , unsafe_allow_html = True
)

# Load Input Data
@st.cache_data
def get_predictions():
    '''Call API to get weather data for prediction'''
    data = format_inputs()
    return data 

# Get inputs 
inputs = get_predictions()
prev_load = inputs[0] # N.Y.C.: NYC load from NYISO.com
prev_dni = inputs[1] # Dni: Current DNI from solarcast
prev_temp = inputs[2] # HourlyDryBulbTemperature: Current NOAA Temp
future_dni = inputs[3] # Dni Future: T to T+90 future DNI from solarcast
future_temp = inputs[4] # HourlyDryBulbTemperature Future:  T to T+90 future NOAA Temp

# Fit into model and get predictions
tranformed_data = tranform_data(inputs)
model = import_model("lstm_cv_final.h5")
prediction = make_prediction(np.array([tranformed_data]), model) # 90 min forecast

# Plot Forecasts
prediction_df = pd.DataFrame({'Min': list(range(5, 95, 5))})
prediction_df['Load'] = prediction.T
prev_load_df = pd.DataFrame({'Min': list(range(-85, 5, 5))})
prev_load_df['Load'] = inputs[0].T
combined_load = prev_load_df.append(prediction_df)


a = (alt.Chart(combined_load)
    .mark_line(point = True)
    .encode(
        alt.X('Min', title = 'Min From Current Time', scale = alt.Scale(domain = [-85, 90])),
        alt.Y('Load', title = 'Load [MWh]'),
    )
)
line = (alt.Chart(pd.DataFrame({'Min': [0]}))
    .mark_rule()
    .encode(
        alt.X('Min', scale = alt.Scale(domain = [-85, 90]))
    )
)
st.altair_chart((line + a), use_container_width=True)

# Export Data
col1, col2 = st.columns(2)

with col1:
    if st.button('Export Data', key = 'electric_forecast_df'):
        with st.spinner("Exporting..."):
            export_forecast = combined_load.to_csv()
            b64 = base64.b64encode(export_forecast.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)

with col2:
    # Get time
    now = datetime.now()
    current_time = now.strftime("%m/%d/%Y %I:%M:%S %p")
    st.markdown(f'<div style="text-align: right;"><em>Last refreshed {current_time}</em></div>', unsafe_allow_html=True)


# Current Weather Conditions
st.header('Current Conditions')
col1, col2 = st.columns(2)



prev_dni = inputs[1] # Dni: Current DNI from solarcast
prev_temp = inputs[2] # HourlyDryBulbTemperature: Current NOAA Temp
future_dni = inputs[3] # Dni Future: T to T+90 future DNI from solarcast
future_temp = inputs[4] # HourlyDryBulbTemperature Future:  T to T+90 future NOAA Temp



# Weather Data
with col1:
    st.markdown('<p style="font-size: 20px;"><b>Projected Temperature | Provided by NOAA<b></p>', unsafe_allow_html=True)
    temp_df = pd.DataFrame({'Min': list(range(5, 95, 5))})
    temp_df['Temp'] = inputs[4].T
    prev_temp_df = pd.DataFrame({'Min': list(range(-85, 5, 5))})
    prev_temp_df['Temp'] = inputs[2].T
    combined = prev_temp_df.append(temp_df)    

    a = (alt.Chart(combined)
        .mark_line(point = True)
        .encode(
            alt.X('Min', title = 'Min From Current Time', scale = alt.Scale(domain = [-85, 90])),
            alt.Y('Temp', title = 'Temperature [°F]'),
        )
    )
    line = (alt.Chart(pd.DataFrame({'Min': [0]}))
        .mark_rule()
        .encode(
            alt.X('Min', scale = alt.Scale(domain = [-85, 90]))
        )
    )
    st.altair_chart((line + a), use_container_width=True)


# Solar Data
with col2:
    st.markdown('<p style="font-size: 20px;"><b>Projected Solar | Provided by Solcast<b></p>', unsafe_allow_html=True)
    temp_df = pd.DataFrame({'Min': list(range(5, 95, 5))})
    temp_df['Solar'] = inputs[3].T
    prev_temp_df = pd.DataFrame({'Min': list(range(-85, 5, 5))})
    prev_temp_df['Solar'] = inputs[1].T
    combined = prev_temp_df.append(temp_df)   

    a = (alt.Chart(combined)
        .mark_line(point = True)
        .encode(
            alt.X('Min', title = 'Min From Current Time', scale = alt.Scale(domain = [-85, 90])),
            alt.Y('Solar', title = 'Solar Irradiance [DNI]'),
        )
    )
    line = (alt.Chart(pd.DataFrame({'Min': [0]}))
        .mark_rule()
        .encode(
            alt.X('Min', scale = alt.Scale(domain = [-85, 90]))
        )
    )
    st.altair_chart((line + a), use_container_width=True)

