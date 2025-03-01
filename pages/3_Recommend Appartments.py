import streamlit as st
import pandas as pd
import plotly.express as px
import pickle
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Recommend Apartments", layout="wide")

# Load datasets correctly
with open('datasets/location_distance.pkl', 'rb') as file:
    location_df = pickle.load(file)

with open('datasets/cosine_sim1.pkl', 'rb') as file:
    cosine_sim1 = pickle.load(file)

with open('datasets/cosine_sim2.pkl', 'rb') as file:
    cosine_sim2 = pickle.load(file)

with open('datasets/cosine_sim3.pkl', 'rb') as file:
    cosine_sim3 = pickle.load(file)

# Recommendation function
def recommend_properties_with_scores(property_name, top_n=5):
    if property_name not in location_df.index:
        return pd.DataFrame(columns=["PropertyName", "SimilarityScore"])

    cosine_sim_matrix = 30 * cosine_sim1 + 20 * cosine_sim2 + 8 * cosine_sim3
    
    # Get similarity scores for the selected property
    sim_scores = list(enumerate(cosine_sim_matrix[location_df.index.get_loc(property_name)]))
    
    # Sort by similarity score
    sorted_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Get top N most similar properties
    top_indices = [i[0] for i in sorted_scores[1:top_n+1]]
    top_scores = [i[1] for i in sorted_scores[1:top_n+1]]
    
    # Retrieve property names using indices
    top_properties = location_df.index[top_indices].tolist()
    
    return pd.DataFrame({'PropertyName': top_properties, 'SimilarityScore': top_scores})

# User Input - Location and Radius
st.title("Select Location and Radius")
selected_location = st.selectbox('Location', sorted(location_df.columns.tolist()), index=sorted(location_df.columns.tolist()).index("Chirag Hospital"))


radius = st.number_input('Radius in Kms', min_value=0.1, step=0.1, value=10.0)

if st.button('Search'):
    filtered_df = location_df[location_df[selected_location] < (radius * 1000)]

    if filtered_df.empty:
        st.text("No properties found.")
    else:
        for index, row in filtered_df.iterrows():
            st.text(f"{index} - {round(row[selected_location] / 1000, 2)} kms")

# Recommendation Section
st.title('Recommend Apartments')
selected_apartment = st.selectbox('Select an apartment', sorted(location_df.index.tolist()))

if st.button("Recommend"):
    recommendation_df = recommend_properties_with_scores(selected_apartment)
    
    if recommendation_df.empty:
        st.warning("No recommendations found.")
    else:
        st.write("Recommended Properties:")
        st.dataframe(recommendation_df)
