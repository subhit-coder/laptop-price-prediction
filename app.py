import streamlit as st
import joblib
import numpy as np
import pandas as pd
# Custom CSS for background and card
def set_bg():
    st.markdown(f"""
    <style>
    .stApp {{
        background: url("https://images.unsplash.com/photo-1517336714731-489689fd1ca8");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    .main-card {{
        background-color: rgba(255, 255, 255, 0.9);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.2);
    }}

    .stButton>button {{
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
        border-radius: 10px;
        padding: 10px 20px;
    }}

    .stSelectbox, .stNumberInput, .stSlider {{
        margin-bottom: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

set_bg()
# Load model and dataset
pipe = joblib.load('pipe.pkl')
df = pd.read_csv('df.csv')

st.title("💻 Laptop Price Predictor")

# Brand
company = st.selectbox('Brand', df['Company'].unique())

# Type of laptop
type = st.selectbox('Type', df['TypeName'].unique())

# RAM
ram = st.selectbox('RAM (in GB)', [2,4,6,8,12,16,24,32,64])

# Weight
weight = st.number_input('Weight of the Laptop')

# Touchscreen
touchscreen = st.selectbox('Touchscreen', ['No','Yes'])

# IPS
ips = st.selectbox('IPS', ['No','Yes'])

# Screen size
screen_size = st.slider('Screen size in inches', 10.0, 18.0, 13.0)

# Resolution
resolution = st.selectbox('Screen Resolution', [
    '1920x1080','1366x768','1600x900','3840x2160',
    '3200x1800','2880x1800','2560x1600','2560x1440','2304x1440'
])

# CPU
cpu = st.selectbox('CPU', df['Cpu brand'].unique())

# HDD
hdd = st.selectbox('HDD (in GB)', [0,128,256,512,1024,2048])

# SSD
ssd = st.selectbox('SSD (in GB)', [0,8,128,256,512,1024])

# GPU
gpu = st.selectbox('GPU', df['Gpu brand'].unique())

# OS
os = st.selectbox('OS', df['os'].unique())

if st.button('Predict Price'):
    # Convert categorical to numeric
    touchscreen = 1 if touchscreen == 'Yes' else 0
    ips = 1 if ips == 'Yes' else 0

    # Calculate PPI
    X_res = int(resolution.split('x')[0])
    Y_res = int(resolution.split('x')[1])
    ppi = ((X_res**2) + (Y_res**2))**0.5 / screen_size

    # Query array
    query = np.array([company, type, ram, weight, touchscreen, ips, ppi, cpu, hdd, ssd, gpu, os])
    query = query.reshape(1,12)

    # Prediction
    predicted_price = int(np.exp(pipe.predict(query)[0]))
    st.success(f"💰 The predicted price of this configuration is ₹{predicted_price}")

