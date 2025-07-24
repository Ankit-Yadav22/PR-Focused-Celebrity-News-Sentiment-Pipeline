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

# Calculate date range: from 15 days ago to today
end_date = datetime.utcnow().date()
start_date = end_date - timedelta(days=15)

# Format as YYYY-MM-DD
from_date = start_date.strftime('%Y-%m-%d')
to_date = end_date.strftime('%Y-%m-%d')

for celeb in celebrities:
    url = (
        "https://newsapi.org/v2/everything?"
        f"q=\"{celeb}\"&"
        f"from={from_date}&"
        f"to={to_date}&"
        "language=en&"
        "sortBy=publishedAt&"
        "pageSize=100&"  # Max allowed per page
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
