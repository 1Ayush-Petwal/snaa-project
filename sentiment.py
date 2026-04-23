from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import ast

# Load data
df = pd.read_csv("public/processed_data.csv")

df['hashtags'] = df['hashtags'].apply(lambda x: ast.literal_eval(x))

analyzer = SentimentIntensityAnalyzer()

# -----------------------------
# Compute sentiment per tweet
# -----------------------------
def get_sentiment(text):
    return analyzer.polarity_scores(text)['compound']

df['sentiment'] = df['clean_text'].apply(get_sentiment)

# -----------------------------
# Aggregate sentiment per user
# -----------------------------
user_sentiment = df.groupby('user_name')['sentiment'].mean().to_dict()

# Save
import pickle
with open("public/user_sentiment.pkl", "wb") as f:
    pickle.dump(user_sentiment, f)

print("Sentiment computed for users:", len(user_sentiment))