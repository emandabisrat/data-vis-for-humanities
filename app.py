import streamlit as st
import json
import time
import re
import pandas as pd
import geopandas as gpd
import praw
import nltk
import plotly.express as px
from wordcloud import WordCloud
from nltk.sentiment import SentimentIntensityAnalyzer
from shapely.geometry import shape


nltk.download("vader_lexicon")
sia = SentimentIntensityAnalyzer()

st.title("Reddit Sentiment Analysis & Immigration Data Visualization")

st.sidebar.header("Search Query!")
query = st.sidebar.text_input("Enter Reddit Search Query:", "Illegal Immigration")
subreddits = st.sidebar.multiselect("Select Subreddits:", ["Trump", "wall", "documented", "deportation", "politics", "rights"], default=["Trump", "wall"])

reddit = praw.Reddit(
    client_id="PV-z6Xrlf6xOzzuAEhUR3w",
    client_secret="tT4gHWHRdxEjGPywp57sRrPlMHL1-w",
    user_agent="SentimentAnalysisBot/1.0 by YourUsername"
)

start_time = 1484870400  
end_time = int(time.time())

@st.cache_data
def fetch_reddit_data():
    data = []
    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        for submission in subreddit.search(query, limit=50):
            if start_time <= submission.created_utc <= end_time:
                data.append({
                    "type": "post",
                    "title": submission.title,
                    "body": submission.selftext,
                    "created_at": submission.created_utc,
                    "subreddit": subreddit_name
                })

            submission.comments.replace_more(limit=0)
            for comment in submission.comments.list():
                data.append({
                    "type": "comment",
                    "body": comment.body,
                    "created_at": comment.created_utc,
                    "subreddit": subreddit_name
                })
            time.sleep(2)  

    return pd.DataFrame(data)

tab1, tab2 = st.tabs(["Reddit Sentiment Analysis", "Immigration Data"])

with tab1:
    st.header("Reddit Sentiment Analysis")
    st.subheader("Analyze the sentiment of Reddit discussions on undocumented immigrants. Press 'Fetch Data' to your left to get posts and comments from Reddit pertaining to the query and subquery of your choice! ")
    st.markdown("<h5 style='color:red;'>After just a couple minutes of scraping the posts, word clouds will appear that show the positive, negataive, and neutral sentiment surrounding your query!</h5>", unsafe_allow_html=True)
    st.sidebar.write("Click to Fetch Reddit Data:")
    
    if st.sidebar.button("Fetch Data"):
        with st.spinner("Fetching data from Reddit..."):
            df_reddit = fetch_reddit_data()
            df_reddit["created_at"] = pd.to_datetime(df_reddit["created_at"], unit="s", errors="coerce")
            df_reddit["cleaned_text"] = df_reddit["body"].astype(str).apply(lambda x: re.sub(r"[^\w\s]", "", x))
            df_reddit["sentiment"] = df_reddit["cleaned_text"].apply(lambda text: sia.polarity_scores(text)["compound"])
            df_reddit["sentiment_vader"] = df_reddit["sentiment"].apply(lambda x: "positive" if x >= 0.05 else "negative" if x <= -0.05 else "neutral")

        sentiment_counts = df_reddit["sentiment_vader"].value_counts()
        st.write("Sentiment Analysis Distribution:", sentiment_counts)
        
        st.subheader("Sentiment Word Clouds")
        col1, col2, col3 = st.columns(3)
        
        sentiments = ["positive", "neutral", "negative"]
        cols = [col1, col2, col3]
        
        for i, sentiment in enumerate(sentiments):
            filtered_df = df_reddit[df_reddit["sentiment_vader"] == sentiment]
            if not filtered_df.empty:
                text = " ".join(filtered_df["body"])
                if text.strip():  
                    wc = WordCloud(width=600, height=300, background_color="white").generate(text)
                    cols[i].image(wc.to_array(), caption=f"{sentiment.capitalize()} Sentiment")
                else:
                    cols[i].write(f"No {sentiment} sentiment data available")
            else:
                cols[i].write(f"No {sentiment} sentiment data available")

with tab2:
    st.header("Undocumented Immigration Data by State")
    st.markdown("<h5 style='color:red;'>Below is a choropleth map that represents the total amount of undocumented immigrants in each state in the U.S. It's interesting to see the changes overtime, especially in California and Texas. Press the play button below!</h5>", unsafe_allow_html=True)
    
    try:
        with open('/Users/emandabisrat/Downloads/data-vis-for-humanities/data/gz_2010_us_040_00_500k (1).json') as f:
            geo_data = json.load(f)
        def simplify_geojson(geo_data, tolerance=0.01):
            for feature in geo_data['features']:
                geometry = shape(feature['geometry'])
                simplified_geometry = geometry.simplify(tolerance)
                feature['geometry'] = simplified_geometry.__geo_interface__
            return geo_data

        simplified_geo_data = simplify_geojson(geo_data, tolerance=0.01)

    except FileNotFoundError:
        st.error("Geographic data file not found. Please check the file path.")
        st.stop()
    
    try:
        states_csv = pd.read_csv("/Users/emandabisrat/Downloads/data-vis-for-humanities/data/CMS-data-undoc-state_2010-2019(1).csv", header=3)
        states_csv = states_csv.drop(index=[510, 511, 512, 513, 514])
        states_csv["Total"] = states_csv["Total"].str.replace(",", "").astype(float)
        states_csv["Year"] = states_csv["Year"].astype(int)
    except FileNotFoundError:
        st.error("Immigration data file not found. Please check the file path.")
        st.stop()
    
    gdf = gpd.GeoDataFrame.from_features(simplified_geo_data["features"])
    gdf["NAME"] = gdf["NAME"].str.upper()
    states_csv["State"] = states_csv["State"].str.upper()
    merged_data = gdf.merge(states_csv, left_on="NAME", right_on="State", how="left")
    merged_data = merged_data.dropna(subset=['Year'])
    merged_data['Year'] = merged_data['Year'].astype(str).str.replace(r'\.0$', '', regex=True)

    fig = px.choropleth(merged_data,
                        geojson=merged_data.geometry,
                        locations=merged_data.index,
                        color='Total',
                        hover_name='NAME',
                        animation_frame='Year',  
                        range_color=(0, merged_data['Total'].max()), 
                        color_continuous_scale='Viridis', 
                        labels={'Total': 'Undocumented Immigrants'},
                        title="Undocumented Immigrants in US States (2010-2019)")
    
    fig.update_layout(
        height=700,  
        width=900, 
        margin={"r": 0, "t": 50, "l": 0, "b": 0},  
        geo=dict(
            scope='usa',
            projection_scale=0.6, 
            center=dict(lat=37.0902, lon=-95.7129), 
            showland=True
        )
    )
    fig.update_traces(marker_line_width=0.5, marker_line_color="white")
    st.plotly_chart(fig, use_container_width=True)  
    