import streamlit as st
import pandas as pd
import plotly.express as px

# Load Netflix data
@st.cache_data
def load_data():
    df = pd.read_csv('netflix_titles.csv')
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filter Netflix Data")
type_filter = st.sidebar.multiselect(
    "Select Type",
    options=df['type'].unique(),
    default=df['type'].unique()
)

genre_filter = st.sidebar.multiselect(
    "Select Genre",
    options=df['listed_in'].unique(),
    default=df['listed_in'].unique()
)

year_filter = st.sidebar.slider(
    "Select Release Year",
    min_value=int(df['release_year'].min()),
    max_value=int(df['release_year'].max()),
    value=(2000, 2020)
)

# Filter data based on selections
filtered_df = df[
    (df['type'].isin(type_filter)) &
    (df['listed_in'].isin(genre_filter)) &
    (df['release_year'].between(year_filter[0], year_filter[1]))
]

# Main dashboard
st.title("🎬 Netflix Data Dashboard")

# KPIs
total_titles = filtered_df.shape[0]
total_movies = filtered_df[filtered_df['type'] == 'Movie'].shape[0]
total_tvshows = filtered_df[filtered_df['type'] == 'TV Show'].shape[0]

st.metric("Total Titles", total_titles)
st.metric("Movies", total_movies)
st.metric("TV Shows", total_tvshows)

st.markdown("---")

# Chart: Titles per Genre
st.subheader("Titles per Genre")
genre_counts = filtered_df['listed_in'].value_counts().head(10)
fig_genre = px.bar(
    x=genre_counts.index,
    y=genre_counts.values,
    labels={'x': 'Genre', 'y': 'Number of Titles'},
    title="Top 10 Genres"
)
st.plotly_chart(fig_genre)

# Chart: Titles Released per Year
st.subheader("Titles Released Over Years")
titles_per_year = filtered_df.groupby('release_year').size()
fig_year = px.line(
    x=titles_per_year.index,
    y=titles_per_year.values,
    labels={'x': 'Release Year', 'y': 'Number of Titles'},
    title="Titles by Release Year"
)
st.plotly_chart(fig_year)

# Table: Top 10 Longest Movies
st.subheader("Top 10 Longest Movies")

# Handle duration column clean-up if needed
if 'duration' in df.columns:
    # Only keep movies and extract the numeric minutes
    movies_df = filtered_df[filtered_df['type'] == 'Movie'].copy()
    movies_df['duration_mins'] = movies_df['duration'].str.extract('(\d+)').astype(float)

    top_longest = movies_df.sort_values('duration_mins', ascending=False).head(10)
    st.dataframe(top_longest[['title', 'duration', 'listed_in', 'release_year']])
else:
    st.warning("Duration data not available.")



