import streamlit as st
import pandas as pd
import numpy as np
import time
from PIL import Image

# Page Config
st.set_page_config(page_title ="Real-Time Electric Load Forecasting",
                    layout="wide",
                    initial_sidebar_state="collapsed",
                    page_icon="⚡")

# Banner Image
image = Image.open('./photos/banner.png')
st.image(image, use_column_width = 'always')

# Title
st.title('About Us')
st.write(
	'''
	_Our mission is to lower electricity prices and improve reliability of the electrical grid by giving operators 
	real-time forecasts to more accurately predict demands of their customers._
	'''
)

# Project Details
with open('./Pages/project_details.md') as file:
    st.write(file.read())


# Team Description
st.header('The Team')
st.write('We are UC Berkeley MIDS students showcasing our final capstone project.')


def show_member(name = '', job = '', image_file = ''):
	'''Display image of the team'''
	image = Image.open(image_file)
	st.image(image, use_column_width = 'always')
	st.markdown(f'<div style="text-align: center;"><b>{name}</b><br>{job}</p>', unsafe_allow_html = True)


mem1, mem2, mem3, mem4, mem5 = st.columns(5)

with mem1: 
	show_member('Emily Fernandes', job = 'Senior Grid Operations Engineer', image_file = './photos/emily.png')

with mem2: 
	show_member('Shuhan Yu', job = 'Financial Analyst', image_file = './photos/shuhan.png')

with mem3: 
	show_member('Sean Furuta', job = 'Data Scientist', image_file = './photos/sean.png')

with mem4: 
	show_member('Melinda Leung', job = 'Senior Data Analyst', image_file = './photos/melinda.png')

with mem5: 
	show_member('Dunny Semwayo', job = 'Project Manager', image_file = './photos/dunny.png')