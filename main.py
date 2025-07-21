import requests
import pandas as pd
from datetime import datetime
from textblob import TextBlob
from dotenv import load_dotenv
import os

load_dotenv() 

API_KEY = os.getenv("API_KEY") 
celebrities = ["Virat Kohli", "MS Dhoni"]
results = []

for celeb in celebrities:
    url = (
        "https://newsapi.org/v2/everything?"
        f"q=\"{celeb}\"&"
        "language=en&"
        "sortBy=publishedAt&"
        "pageSize=10&"
        f"apiKey={API_KEY}"
    )
    response = requests.get(url)
    articles = response.json().get("articles", [])
    
    for article in articles:
        results.append({
            "date": article.get("publishedAt", "")[:10],
            "celebrity": celeb,
            "headline": article.get("title", ""),
            "source": article.get("source", {}).get("name", ""),
            "url": article.get("url", "")
        })

df = pd.DataFrame(results)
display(df)  # For Databricks notebooks



def get_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "Good"
    elif polarity < -0.1:
        return "Bad"
    else:
        return "Neutral"

df['sentiment'] = df['headline'].apply(get_sentiment)
display(df)

# Group by celebrity and sentiment to count occurrences
sentiment_counts = df.groupby(['celebrity', 'sentiment']).size().reset_index(name='count')

# Total headline count per celebrity
total_counts = sentiment_counts.groupby('celebrity')['count'].transform('sum')

# Calculate percentage for each sentiment per celebrity
sentiment_counts['percentage'] = 100 * sentiment_counts['count'] / total_counts

# Optional: Sort for better readability
sentiment_counts = sentiment_counts.sort_values(['celebrity', 'sentiment']).reset_index(drop=True)

display(sentiment_counts)
