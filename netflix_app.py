import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Set Streamlit page config
st.set_page_config(
    page_title="Netflix Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom background using Streamlit HTML hack
def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://images.unsplash.com/photo-1617384521063-6a7e81d20b6c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80");
             background-attachment: fixed;
             background-size: cover;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_bg_from_url()

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
# NEW: Rating filter
if 'rating' in df.columns:  # Ensure the "rating" column exists in the dataset
    rating_filter = st.sidebar.multiselect(
        "Select Rating",
        options=df['rating'].dropna().unique(),  # Drop NaN values before listing unique ratings
        default=df['rating'].dropna().unique()  # Default to all available ratings
    )
else:
    st.sidebar.warning("Rating column not found in the dataset.")
    rating_filter = df['rating'].unique()  # In case the column doesn't exist, fallback to all ratings
# Filter data
filtered_df = df[
    (df['type'].isin(type_filter)) &
    (df['release_year'].between(year_filter[0], year_filter[1]))
]

# Main Title
st.title("🎥 Netflix Global Content Dashboard")
st.markdown("##### Powered by Streamlit + Plotly | Data Source: Netflix Titles")

# KPIs
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Titles", filtered_df.shape[0])
with col2:
    st.metric("Movies", filtered_df[filtered_df['type'] == 'Movie'].shape[0])
with col3:
    st.metric("TV Shows", filtered_df[filtered_df['type'] == 'TV Show'].shape[0])

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", 
    "🎭 Genre Insights", 
    "⏱️ Movie Durations", 
    "🎯 Ratings Analysis", 
    "🌍 Country Insights"
])

# 1. Overview Tab
with tab1:
    st.subheader("Titles Released by Year")
    titles_per_year = filtered_df.groupby('release_year').size()
    fig_year = px.area(
        x=titles_per_year.index,
        y=titles_per_year.values,
        labels={'x': 'Release Year', 'y': 'Number of Titles'},
        title="Content Growth Over Time",
        template="plotly_dark",
    )
    st.plotly_chart(fig_year, use_container_width=True)

    st.subheader("Movies vs TV Shows")
    type_counts = filtered_df['type'].value_counts()
    fig_type = px.pie(
        names=type_counts.index,
        values=type_counts.values,
        title="Distribution: Movies vs TV Shows",
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig_type, use_container_width=True)

# 2. Genre Insights
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

    st.subheader("Word Cloud of Titles")
    text = " ".join(filtered_df['title'].dropna())
    wordcloud = WordCloud(
        background_color='white',
        max_words=100,
        colormap='Reds'
    ).generate(text)
    fig_wc, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig_wc)

# 3. Movie Durations
with tab3:
    st.subheader("Longest Movies on Netflix")
    if 'duration' in df.columns:
        movies_df = filtered_df[filtered_df['type'] == 'Movie'].copy()
        movies_df['duration_mins'] = movies_df['duration'].str.extract('(\d+)').astype(float)
        longest_movies = movies_df.sort_values('duration_mins', ascending=False).head(10)
        st.dataframe(longest_movies[['title', 'duration', 'listed_in', 'release_year']])

        avg_duration = movies_df['duration_mins'].mean()
        st.metric("Average Movie Duration (minutes)", f"{avg_duration:.2f}")
    else:
        st.warning("Duration column is missing in the dataset.")

# 4. Ratings Analysis
with tab4:
    st.subheader("Ratings Distribution")
    if 'rating' in df.columns:
        ratings_count = filtered_df['rating'].value_counts().head(10)
        fig_ratings = px.bar(
            x=ratings_count.index,
            y=ratings_count.values,
            labels={'x': 'Rating', 'y': 'Number of Titles'},
            title="Top 10 Ratings on Netflix",
            color=ratings_count.values,
            color_continuous_scale='blues',
            template="plotly_white"
        )
        st.plotly_chart(fig_ratings, use_container_width=True)
    else:
        st.warning("Rating column not found.")

# 5. Country Insights (with Choropleth Map)
with tab5:
    st.subheader("Global Distribution of Netflix Content")
    if 'country' in df.columns:
        country_df = filtered_df.copy()
        country_df['main_country'] = country_df['country'].str.split(',').str[0]
        
        country_counts = country_df['main_country'].value_counts().reset_index()
        country_counts.columns = ['country', 'count']

        fig_choropleth = px.choropleth(
            country_counts,
            locations='country',
            locationmode='country names',
            color='count',
            color_continuous_scale='reds',
            title="Netflix Titles by Country",
            labels={'count': 'Number of Titles'},
            template="plotly_white",
        )
        fig_choropleth.update_layout(
            margin={"r":0,"t":30,"l":0,"b":0}
        )
        st.plotly_chart(fig_choropleth, use_container_width=True)
    else:
        st.warning("Country data not available.")

st.markdown("---")
st.caption("Built with ❤️ using Streamlit | Netflix Titles Data")

