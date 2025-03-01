import streamlit as st
import pickle
import pandas as pd

st.set_page_config(page_title="Property Price Prediction", layout="wide")

# Load Data
with open('df.pkl', 'rb') as file:
    df = pickle.load(file)

with open('pipeline.pkl', 'rb') as file:
    model_pipeline = pickle.load(file)

st.header("🏠 Enter Property Details for Prediction")

# User Inputs
property_type = st.selectbox('Property Type', ['flat', 'house'])
sector = st.selectbox('Sector', sorted(df['sector'].unique().tolist()))
bedroom = float(st.selectbox('Number of Bedrooms', sorted(df['bedRoom'].unique().tolist())))
bathroom = float(st.selectbox('Number of Bathrooms', sorted(df['bathroom'].unique().tolist())))
balcony = st.selectbox('Balconies', sorted(df['balcony'].unique().tolist()))
property_age = st.selectbox('Property Age', sorted(df['agePossession'].unique().tolist()))
built_up_area = float(st.number_input("Built-up Area (sqft)", min_value=1.0))
servant_room = 0 if st.selectbox('Servant Room', ["Yes", "No"]) == "No" else 1
store_room = 0 if st.selectbox('Store Room', ["Yes", "No"]) == "No" else 1
furnishing_type = st.selectbox('Furnishing Type', sorted(df['furnishing_type'].unique().tolist()))
luxury_category = st.selectbox('Luxury Category', sorted(df['luxury_category'].unique().tolist()))
floor_category = st.selectbox('Floor Category', sorted(df['floor_category'].unique().tolist()))

# **Predict Button**
if st.button('💰 Predict Price'):
    # Create Input DataFrame
    input_data = pd.DataFrame({
        'property_type': [property_type],
        'sector': [sector],
        'bedRoom': [bedroom],
        'bathroom': [bathroom],
        'balcony': [balcony],
        'agePossession': [property_age],
        'built_up_area': [built_up_area],
        'servant room': [servant_room],
        'store room': [store_room],
        'furnishing_type': [furnishing_type],
        'luxury_category': [luxury_category],
        'floor_category': [floor_category]
    })

    # **Perform Prediction**
    base_price = model_pipeline.predict(input_data)[0]
    low = max(0, base_price - 0.22)
    high = base_price + 0.22

    # **Display Prediction**
    st.success(f"💲 Estimated Price Range: **{round(low, 2)} cr** - **{round(high, 2)} cr**")
