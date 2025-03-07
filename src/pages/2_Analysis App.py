import streamlit as st
import pandas as pd
import plotly.express as px
import pickle
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns

# Set page configuration
st.set_page_config(page_title="Real Estate Analytics", layout="wide")
st.title("📊 Real Estate Analytics Dashboard")

# Load datasets
DATA_PATH = 'datasets/data_viz1.csv'
FEATURE_TEXT_PATH = 'datasets/feature_text.pkl'

df = pd.read_csv(DATA_PATH)
feature_text = pickle.load(open(FEATURE_TEXT_PATH, 'rb'))

# Handle missing values
df = df.dropna(subset=['latitude', 'longitude'])
df.fillna(0, inplace=True)

# Compute initial map center
center_lat = df["latitude"].mean()
center_lon = df["longitude"].mean()
default_zoom = 12

# Initialize session state for map
if "map_center" not in st.session_state:
    st.session_state.map_center = {"lat": center_lat, "lon": center_lon}
if "map_zoom" not in st.session_state:
    st.session_state.map_zoom = default_zoom

# Box plot for BHK price comparison
st.header("🏠 BHK Price Range Comparison")
temp_df = df[df['bedRoom'] <= 4]
fig_bhk = px.box(temp_df, x='bedRoom', y='price')
st.plotly_chart(fig_bhk, use_container_width=True)

# Sector Price per Sqft Geomap
st.header("📍 Sector Price per Sqft Geomap")
with st.sidebar:
    st.subheader("🔄 Map Controls")
    if st.button("Reset View"):
        st.session_state.map_center = {"lat": center_lat, "lon": center_lon}
        st.session_state.map_zoom = default_zoom
        st.experimental_rerun()

# Group data by sector
group_df = df.groupby('sector')[['price', 'price_per_sqft', 'built_up_area', 'latitude', 'longitude']].mean()

# Create map visualization
fig_map = px.scatter_mapbox(
    group_df, lat="latitude", lon="longitude", color="price_per_sqft",
    size="built_up_area", color_continuous_scale=px.colors.cyclical.IceFire,
    zoom=st.session_state.map_zoom,
    center={"lat": st.session_state.map_center["lat"], "lon": st.session_state.map_center["lon"]},
    mapbox_style="open-street-map", width=800, height=700,
    hover_name=group_df.index
)
st.plotly_chart(fig_map)

# Features Word Cloud
st.header("📝 Features Word Cloud")
wordcloud = WordCloud(width=600, height=400, background_color="white", min_font_size=10).generate(feature_text)
fig_wc, ax = plt.subplots(figsize=(8, 8))
ax.imshow(wordcloud, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig_wc)

# Property Type Scatter Plot
st.header("📈 Area vs Price for Property Type")
property_type = st.selectbox("Select Property Type", ['Flat', 'House'])
filtered_df = df[df['property_type'].str.lower() == property_type.lower()]
fig_area_price = px.scatter(filtered_df, x="built_up_area", y="price", color="bedRoom", title="Area vs Price")
st.plotly_chart(fig_area_price)

# BHK Distribution Pie Chart
st.header(" BHK Distribution")
sector_options = ['Overall'] + df['sector'].unique().tolist()
selected_sector = st.selectbox("Select Sector", sector_options)
filtered_pie_df = df if selected_sector == "Overall" else df[df['sector'] == selected_sector]
fig_bhk_pie = px.pie(filtered_pie_df, names='bedRoom')
st.plotly_chart(fig_bhk_pie, use_container_width=True)

# Price Distribution for Houses & Flats
st.header("🏡 Continuous Price Distribution for House & Flat")
fig_price_dist, ax = plt.subplots(figsize=(10, 5))
sns.kdeplot(df[df['property_type'] == 'house']['price'], shade=True, color="blue", label="House", ax=ax)
sns.kdeplot(df[df['property_type'] == 'flat']['price'], shade=True, color="red", label="Flat", ax=ax)
ax.set_title("Price Distribution for Houses & Flats")
ax.set_xlabel("Price")
ax.set_ylabel("Density")
ax.legend()
st.pyplot(fig_price_dist)
