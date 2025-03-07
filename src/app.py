import streamlit as st
import pandas as pd
import plotly.express as px
import pickle
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns

# Page Config
st.set_page_config(page_title="Real Estate Dashboard", layout="wide")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv('datasets/data_viz1.csv')
    df = df.dropna(subset=['latitude', 'longitude'])
    df.fillna(0, inplace=True)  # Fill missing values
    return df

@st.cache_data
def load_pickles():
    feature_text = pickle.load(open('datasets/feature_text.pkl', 'rb'))
    location_df = pickle.load(open('datasets/location_distance.pkl', 'rb'))
    cosine_sim1 = pickle.load(open('datasets/cosine_sim1.pkl', 'rb'))
    cosine_sim2 = pickle.load(open('datasets/cosine_sim2.pkl', 'rb'))
    cosine_sim3 = pickle.load(open('datasets/cosine_sim3.pkl', 'rb'))
    return feature_text, location_df, cosine_sim1, cosine_sim2, cosine_sim3

df = load_data()
feature_text, location_df, cosine_sim1, cosine_sim2, cosine_sim3 = load_pickles()

# Sidebar Navigation
st.sidebar.title("🏠 Navigation")
page = st.sidebar.radio("Go to:", ["🏡 Home", "📊 Insights", "🔍 Predict Price", "🏆 Recommendations"])

# Home Page
if page == "🏡 Home":
    st.title("Welcome to the Real Estate Dashboard")
    st.markdown("This dashboard provides insights, predictions, and recommendations for real estate properties.")
    

# Insights Page
elif page == "📊 Insights":
    st.title("📊 Real Estate Analytics")

    # Price Range Comparison
    temp_df = df[df['bedRoom'] <= 4]
    fig3 = px.box(temp_df, x='bedRoom', y='price', title='BHK Price Range Comparison')
    st.plotly_chart(fig3, use_container_width=True)

    # Price Per Sqft Geomap
    st.header('📍 Sector Price Per Sqft')
    group_df = df.groupby('sector')[['price', 'price_per_sqft', 'built_up_area', 'latitude', 'longitude']].mean()

    fig = px.scatter_mapbox(
        group_df, lat="latitude", lon="longitude", color="price_per_sqft",
        size="built_up_area", color_continuous_scale=px.colors.cyclical.IceFire,
        mapbox_style="open-street-map", zoom=12, width=800, height=700, hover_name=group_df.index
    )
    st.plotly_chart(fig)

    # WordCloud for Features
    st.title('🌟 Features Word Cloud')
    wordcloud = WordCloud(width=600, height=400, background_color="white", min_font_size=10).generate(feature_text)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

# Prediction Page
elif page == "🔍 Predict Price":
    st.title("📈 Property Price Prediction")
    

    property_type = st.selectbox('Select Property Type', ['Flat', 'House'])
    built_up_area = st.number_input("Built-up Area (sqft)", min_value=100, max_value=10000, step=100)
    bedrooms = st.slider("Number of Bedrooms", 1, 5, 3)
    location = st.selectbox('Select Sector', df['sector'].unique())

    if st.button("Predict Price"):
        st.success(f"Estimated Price: ₹{(built_up_area * bedrooms * 2000):,.2f}")  # Dummy calculation

# Recommendations Page
elif page == "🏆 Recommendations":
    st.title("🏆 Recommend Apartments")

    selected_apartment = st.selectbox('Select an Apartment', sorted(location_df.index.tolist()))

    def recommend_properties(property_name, top_n=5):
        if property_name not in location_df.index:
            return pd.DataFrame(columns=["PropertyName", "SimilarityScore"])

        cosine_sim_matrix = 30 * cosine_sim1 + 20 * cosine_sim2 + 8 * cosine_sim3
        sim_scores = list(enumerate(cosine_sim_matrix[location_df.index.get_loc(property_name)]))
        sorted_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        top_indices = [i[0] for i in sorted_scores[1:top_n+1]]
        top_scores = [i[1] for i in sorted_scores[1:top_n+1]]
        top_properties = location_df.index[top_indices].tolist()

        return pd.DataFrame({'PropertyName': top_properties, 'SimilarityScore': top_scores})

    if st.button("Get Recommendations"):
        recommendation_df = recommend_properties(selected_apartment)
        if recommendation_df.empty:
            st.warning("No recommendations found.")
        else:
            st.dataframe(recommendation_df)
