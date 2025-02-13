import streamlit as st
import pickle
import pandas as pd
import numpy as np

st.set_page_config(page_title="Recommend Apartments")

# Load data safely
try:
    with open('datasets/location_distance.pkl', 'rb') as file:
        location_df = pickle.load(file)

    if not isinstance(location_df, pd.DataFrame):
        raise ValueError("Pickle file does not contain a valid Pandas DataFrame!")

except Exception as e:
    st.error(f"Error loading location data: {e}")
    st.stop()

# Load similarity matrices
cosine_sim1 = pickle.load(open('datasets/cosine_sim1.pkl', 'rb'))
cosine_sim2 = pickle.load(open('datasets/cosine_sim2.pkl', 'rb'))
cosine_sim3 = pickle.load(open('datasets/cosine_sim3.pkl', 'rb'))

# Ensure similarity matrices have the same dimensions
if not (cosine_sim1.shape == cosine_sim2.shape == cosine_sim3.shape):
    st.error("Error: Similarity matrices have mismatched dimensions!")
    st.stop()

def recommend_properties_with_scores(property_name, top_n=5):
    cosine_sim_matrix = 0.5 * cosine_sim1 + 0.8 * cosine_sim2 + 1 * cosine_sim3

    try:
        property_index = location_df.index.get_loc(property_name)
        sim_scores = list(enumerate(cosine_sim_matrix[property_index]))

        sorted_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        top_indices = [i[0] for i in sorted_scores[1:top_n + 1]]
        top_scores = [i[1] for i in sorted_scores[1:top_n + 1]]

        # Use `.iloc[]` to properly fetch property names
        top_properties = location_df.iloc[top_indices].index.tolist()

        return pd.DataFrame({'PropertyName': top_properties, 'SimilarityScore': top_scores})

    except KeyError:
        st.error("Property not found in dataset!")
        return pd.DataFrame()

st.title('Select Location and Radius')

selected_location = st.selectbox('Location', sorted(location_df.columns.to_list()))
radius = st.number_input('Radius in Kms')

if st.button('Search'):
    if selected_location in location_df.columns:
        result_ser = location_df[location_df[selected_location] < radius * 1000][selected_location].sort_values()
        for key, value in result_ser.items():
            st.text(f"{key} - {round(value / 1000)} kms")
    else:
        st.error("Selected location is not in the dataset!")

st.title('Recommend Apartments')
selected_apartment = st.selectbox('Select an apartment', sorted(location_df.index.to_list()))

if st.button('Recommend'):
    recommendation_df = recommend_properties_with_scores(selected_apartment)
    st.dataframe(recommendation_df)
