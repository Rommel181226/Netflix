import streamlit as st
import pandas as pd
import plotly.express as px

# Load Netflix Data
@st.cache_data
def load_data():
    df = pd.read_csv('netflix_titles.csv')
    return df

df = load_data()

# Sidebar
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg", width=150)
st.sidebar.title("🎬 Netflix Dashboard")
st.sidebar.markdown("Analyze Netflix content trends 📈")

# Sidebar filters
st.sidebar.header("Filter Data")
type_filter = st.sidebar.multiselect(
    "Select Type",
    options=df['type'].unique(),
    default=df['type'].unique()
)

year_filter = st.sidebar.slider(
    "Release Year",
    min_value=int(df['release_year'].min()),
    max_value=int(df['release_year'].max()),
    value=(2000, 2020)
)

# Filter data
filtered_df = df[
    (df['type'].isin(type_filter)) &
    (df['release_year'].between(year_filter[0], year_filter[1]))
]

# Main Page
st.title("🎥 Netflix Data Dashboard")
st.markdown("An interactive dashboard to explore Netflix titles.")

# KPIs
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Titles", filtered_df.shape[0])
with col2:
    st.metric("Movies", filtered_df[filtered_df['type'] == 'Movie'].shape[0])
with col3:
    st.metric("TV Shows", filtered_df[filtered_df['type'] == 'TV Show'].shape[0])

st.markdown("---")

# Tabs for better layout
tab1, tab2, tab3 = st.tabs(["Overview 📊", "Genre Insights 🎭", "Movie Durations ⏱️"])

with tab1:
    st.subheader("Titles by Release Year")
    titles_per_year = filtered_df.groupby('release_year').size()
    fig_year = px.area(
        x=titles_per_year.index,
        y=titles_per_year.values,
        labels={'x': 'Release Year', 'y': 'Number of Titles'},
        title="Content Growth Over Time",
        template="plotly_dark",
    )
    st.plotly_chart(fig_year, use_container_width=True)

with tab2:
    st.subheader("Top 10 Genres")
    top_genres = filtered_df['listed_in'].value_counts().head(10)
    fig_genre = px.bar(
        x=top_genres.values,
        y=top_genres.index,
        orientation='h',
        labels={'x': 'Number of Titles', 'y': 'Genre'},
        title="Top Genres on Netflix",
        template="plotly_white",
        color=top_genres.values,
        color_continuous_scale='reds'
    )
    st.plotly_chart(fig_genre, use_container_width=True)

with tab3:
    st.subheader("Longest Movies on Netflix")
    if 'duration' in df.columns:
        movies_df = filtered_df[filtered_df['type'] == 'Movie'].copy()
        movies_df['duration_mins'] = movies_df['duration'].str.extract('(\d+)').astype(float)
        longest_movies = movies_df.sort_values('duration_mins', ascending=False).head(10)
        st.dataframe(longest_movies[['title', 'duration', 'listed_in', 'release_year']])
    else:
        st.warning("Duration column is missing in the dataset.")

st.markdown("---")
st.caption("Built with ❤️ using Streamlit | Data: Netflix Titles")
