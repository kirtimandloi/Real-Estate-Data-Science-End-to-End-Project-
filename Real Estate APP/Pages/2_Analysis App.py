import streamlit as st
import pandas as pd
import plotly.express as px
import pickle
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Plotting Demo")

st.title('Analytics')

# Load dataset
new_df = pd.read_csv('datasets/data_viz1.csv')

# Convert numeric columns (handling any non-numeric values)
numeric_columns = ['price', 'price_per_sqft', 'built_up_area', 'latitude', 'longitude']
new_df[numeric_columns] = new_df[numeric_columns].apply(pd.to_numeric, errors='coerce')

# Drop rows with NaN values after conversion
new_df.dropna(subset=numeric_columns, inplace=True)

# Group by 'sector' and compute the mean
group_df = new_df.groupby('sector', as_index=True)[numeric_columns].mean()

# Load feature text for word cloud
feature_text = pickle.load(open('datasets/feature_text.pkl', 'rb'))

### 📌 Section: Price per Sqft Geomap ###
st.header('Sector Price per Sqft Geomap')
fig = px.scatter_mapbox(
    group_df, lat="latitude", lon="longitude", color="price_per_sqft", size='built_up_area',
    color_continuous_scale=px.colors.cyclical.IceFire, zoom=10,
    mapbox_style="open-street-map", width=1200, height=700, hover_name=group_df.index
)
st.plotly_chart(fig, use_container_width=True)

### 📌 Section: Features WordCloud ###
st.header('Features Wordcloud')

wordcloud = WordCloud(
    width=800, height=800, background_color='black',
    stopwords=set(['s']), min_font_size=10
).generate(feature_text)

fig_wc, ax_wc = plt.subplots(figsize=(8, 8))
ax_wc.imshow(wordcloud, interpolation='bilinear')
ax_wc.axis("off")
st.pyplot(fig_wc)

### 📌 Section: Area Vs Price ###
st.header('Area Vs Price')

property_type = st.selectbox('Select Property Type', ['flat', 'house'])

fig1 = px.scatter(
    new_df[new_df['property_type'] == property_type],
    x="built_up_area", y="price", color="bedRoom",
    title="Area Vs Price"
)
st.plotly_chart(fig1, use_container_width=True)

### 📌 Section: BHK Pie Chart ###
st.header('BHK Pie Chart')

sector_options = new_df['sector'].unique().tolist()
sector_options.insert(0, 'overall')

selected_sector = st.selectbox('Select Sector', sector_options)

fig2 = px.pie(
    new_df if selected_sector == 'overall' else new_df[new_df['sector'] == selected_sector],
    names='bedRoom'
)
st.plotly_chart(fig2, use_container_width=True)

### 📌 Section: Side by Side BHK Price Comparison ###
st.header('Side by Side BHK Price Comparison')

fig3 = px.box(new_df[new_df['bedRoom'] <= 4], x='bedRoom', y='price', title='BHK Price Range')
st.plotly_chart(fig3, use_container_width=True)

### 📌 Section: Side by Side Distplot for Property Type ###
st.header('Side by Side Distplot for Property Type')

fig4, ax_dist = plt.subplots(figsize=(10, 4))
sns.histplot(new_df[new_df['property_type'] == 'house']['price'], label='house', kde=True, ax=ax_dist)
sns.histplot(new_df[new_df['property_type'] == 'flat']['price'], label='flat', kde=True, ax=ax_dist)
ax_dist.legend()
st.pyplot(fig4)
