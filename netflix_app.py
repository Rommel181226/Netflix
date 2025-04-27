import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# Load and preprocess the data
df = pd.read_csv('netflix_titles.csv')
df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
df['year_added'] = df['date_added'].dt.year
df['month_added'] = df['date_added'].dt.month

# Check column names
#st.write("Columns in DataFrame:", df.columns)

# Genre extractor function
def extract_genres(genre_series):
    genres = genre_series.dropna().str.split(', ')
    return Counter([genre for sublist in genres for genre in sublist])

# Streamlit Layout
st.title("📺 Netflix Data Analysis")

# Create a sidebar with options
st.sidebar.header("Filter Options")
selected_country = st.sidebar.selectbox('Select Country:', ['All'] + list(df['country'].dropna().unique()))
selected_year = st.sidebar.selectbox('Select Year:', ['All'] + sorted(df['year_added'].dropna().unique().tolist()))

# Filter data based on the user's choice
if selected_country != 'All':
    df = df[df['country'] == selected_country]

if selected_year != 'All':
    df = df[df['year_added'] == selected_year]

# Display a pie chart for Movies vs TV Shows
st.subheader("📊 Movies vs TV Shows Breakdown")
fig, ax = plt.subplots(figsize=(6, 6))
df['type'].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=['#ff6f61', '#6b5b95'], startangle=90, ax=ax)
ax.set_title('Movies vs TV Shows')
ax.set_ylabel('')
st.pyplot(fig)

# Display a bar chart for movies by year
st.subheader("📅 Number of Titles Added by Year")
fig2, ax2 = plt.subplots(figsize=(8, 6))
df['year_added'].value_counts().sort_index().plot(kind='bar', color='#6b5b95', ax=ax2)
ax2.set_title('Number of Titles Added by Year')
ax2.set_xlabel('Year')
ax2.set_ylabel('Count')
st.pyplot(fig2)

# Display top 10 popular genres
st.subheader("🔍 Top 10 Genres")
# Check if 'genres' column exists
if 'genres' in df.columns:
    genres_count = extract_genres(df['genres'])
    top_10_genres = dict(genres_count.most_common(10))

    fig3, ax3 = plt.subplots(figsize=(8, 6))
    ax3.bar(top_10_genres.keys(), top_10_genres.values(), color='#ff6f61')
    ax3.set_title('Top 10 Netflix Genres')
    ax3.set_xlabel('Genres')
    ax3.set_ylabel('Frequency')
    plt.xticks(rotation=45)
    st.pyplot(fig3)
else:
    st.error("The 'genres' column is missing in the dataset!")
else:
    st.info("Please upload a CSV file to get started.")
# Display the table of filtered data
st.subheader("📋 Netflix Titles Preview")
st.dataframe(df[['title', 'type', 'year_added', 'rating']].head())

# Add a download button for the filtered data
csv = df[['title', 'type', 'year_added', 'rating']].to_csv(index=False)
st.download_button(label="Download Filtered Data", data=csv, file_name='filtered_netflix_titles.csv', mime='text/csv')
