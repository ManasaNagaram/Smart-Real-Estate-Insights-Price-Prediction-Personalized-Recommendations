
import streamlit as st
import pandas as pd
import pickle

st.set_page_config(page_title="🏠 Apartment Recommender", layout="wide")

# Load data with caching
@st.cache_data
def load_data():
    with open('datasets/location_distance.pkl', 'rb') as file:
        location_df = pickle.load(file)
    
    with open('datasets/cosine_sim1.pkl', 'rb') as file:
        cosine_sim1 = pickle.load(file)

    with open('datasets/cosine_sim2.pkl', 'rb') as file:
        cosine_sim2 = pickle.load(file)

    with open('datasets/cosine_sim3.pkl', 'rb') as file:
        cosine_sim3 = pickle.load(file)

    return location_df, cosine_sim1, cosine_sim2, cosine_sim3

location_df, cosine_sim1, cosine_sim2, cosine_sim3 = load_data()

# Compute weighted similarity matrix
cosine_sim_matrix = 30 * cosine_sim1 + 20 * cosine_sim2 + 8 * cosine_sim3

# Function to recommend apartments
def recommend_properties(property_name, top_n=5):
    if property_name not in location_df.index:
        return pd.DataFrame(columns=["Property Name", "Similarity Score"])

    # Get similarity scores
    sim_scores = list(enumerate(cosine_sim_matrix[location_df.index.get_loc(property_name)]))
    sorted_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Get top recommendations
    top_indices = [i[0] for i in sorted_scores[1:top_n+1]]
    top_scores = [i[1] for i in sorted_scores[1:top_n+1]]
    top_properties = location_df.index[top_indices].tolist()

    return pd.DataFrame({'Property Name': top_properties, 'Similarity Score': top_scores})

# UI - Header
st.title("🏠 Apartment Recommender")
st.markdown("Find the best apartments based on location and similarity.")

# **Sidebar for Inputs**
st.sidebar.header("🔍 Search Nearby Apartments")

selected_location = st.sidebar.selectbox('📍 Select a location:', sorted(location_df.columns.tolist()), index=sorted(location_df.columns.tolist()).index("Chirag Hospital"))
radius = st.sidebar.slider('📏 Radius (in km):', min_value=1, max_value=50, value=10)

if st.sidebar.button('Search'):
    filtered_df = location_df[location_df[selected_location] < (radius * 1000)]
    
    st.subheader(f"🏙️ Apartments within {radius} km of {selected_location}")
    if filtered_df.empty:
        st.warning("No properties found within this radius.")
    else:
        st.dataframe(filtered_df[selected_location].sort_values().apply(lambda x: f"{x / 1000:.2f} km"))

# **Main Page for Recommendations**
st.header("🏢 Recommend Similar Apartments")

selected_apartment = st.selectbox('🏠 Select an apartment:', sorted(location_df.index.tolist()), index=0)

if st.button("Get Recommendations"):
    recommendations = recommend_properties(selected_apartment)
    
    if recommendations.empty:
        st.warning("No recommendations found.")
    else:
        st.write(f"🔹 **Top recommended apartments similar to {selected_apartment}:**")
        st.dataframe(recommendations.style.format({"Similarity Score": "{:.2f}"}))
