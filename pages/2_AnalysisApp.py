import streamlit as st
import pandas as pd
import plotly.express as px
import pickle
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as  sns



st.set_page_config(page_title="Plotting Demo", layout="wide")
st.title("📊 Real Estate Analytics")

# Load data
file_path = 'datasets/data_viz1.csv'  # Adjust path if needed
df = pd.read_csv(file_path)
feature_text = pickle.load(open('datasets/feature_text.pkl','rb'))


# Handle missing lat/lon values
df = df.dropna(subset=['latitude', 'longitude'])
df.fillna(0, inplace=True)  # Fill other missing values with 0

# Compute initial center
center_lat = df["latitude"].mean()
center_lon = df["longitude"].mean()
default_zoom = 12  # Default zoom level

# Initialize session state for map center and zoom
if "map_center" not in st.session_state:
    st.session_state.map_center = {"lat": center_lat, "lon": center_lon}
if "map_zoom" not in st.session_state:
    st.session_state.map_zoom = default_zoom

st.header('Sector Price per sqft Geomap')
# Sidebar controls
with st.sidebar:
    st.subheader("🔄 Map Controls")
    if st.button("Reset View"):
        st.session_state.map_center = {"lat": center_lat, "lon": center_lon}
        st.session_state.map_zoom = default_zoom
        st.experimental_rerun()  # Refresh UI to apply changes

# Group data by sector
group_df = df.groupby('sector')[['price', 'price_per_sqft', 'built_up_area', 'latitude', 'longitude']].mean()

# Create map visualization
fig = px.scatter_mapbox(
    group_df,
    lat="latitude",
    lon="longitude",
    color="price_per_sqft",
    size="built_up_area",
    color_continuous_scale=px.colors.cyclical.IceFire,
    zoom=st.session_state.map_zoom,  # Use session state for zoom
    center={"lat": st.session_state.map_center["lat"], "lon": st.session_state.map_center["lon"]},  # Fix center
    mapbox_style="open-street-map",
    width=800,
    height=700,
    hover_name=group_df.index
)

# Enable interactive controls
fig.update_layout(dragmode="zoom")


# Display in Streamlit
st.plotly_chart(fig)

st.title('Featues word cloud')
wordcloud = WordCloud(
    width=600, height=400,
    background_color="white",
   
    min_font_size=10
).generate(feature_text)

# Plot the WordCloud
fig, ax = plt.subplots(figsize=(8, 8))
ax.imshow(wordcloud, interpolation="bilinear")
ax.axis("off")

# Display in Streamlit
st.pyplot(fig)

property_type = st.selectbox('Select Property Type',['flat','house'])

if property_type == 'house':
    fig1 = px.scatter(
        df[df['property_type']=='house'],
        x="built_up_area", y="price", color="bedRoom", title="Area Vs Price"
    )
    st.plotly_chart(fig1)
else:
    fig1 = px.scatter(
        df[df['property_type']=='flat'],
        x="built_up_area", y="price", color="bedRoom", title="Area Vs Price"
    )
    st.plotly_chart(fig1)


st.header('BHK Pie chart')
sector_options = df['sector'].unique().tolist()
sector_options.insert(0,"overall")
seleced_sector = st.selectbox('Select Sector',sector_options)
if seleced_sector =="overall":
    fig2 = px.pie(df,names = 'bedRoom',title = 'Total Bill Amount by Day')
    st.plotly_chart(fig2,use_container_width = True)
else:
    fig2 = px.pie(df[df['sector']==seleced_sector],names = 'bedRoom',title = 'Total Bill Amount by Day')
    st.plotly_chart(fig2,use_container_width = True)



st.header('Side by side Bhk price comparison')
temp_df = df[df['bedRoom'] <= 4]

fig3= px.box(temp_df, x='bedRoom', y='price', title='BHK Price Range')

st.plotly_chart(fig3,use_container_width = True)




st.header('🏠 Continuous Price Distribution for House & Flat')

# Create figure
fig, ax = plt.subplots(figsize=(10, 5))

# KDE Plots (Continuous Distribution)
sns.kdeplot(df[df['property_type'] == 'house']['price'], shade=True, color="blue", label="House", ax=ax)
sns.kdeplot(df[df['property_type'] == 'flat']['price'], shade=True, color="red", label="Flat", ax=ax)

# Customize plot
ax.set_title("Price Distribution for Houses & Flats")
ax.set_xlabel("Price")
ax.set_ylabel("Density")
ax.legend()  # Show legend for labels

# Display in Streamlit
st.pyplot(fig)
