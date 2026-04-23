import pandas as pd
import re

df = pd.read_csv("public/Political_tweets.csv")

df = df[['user_name', 'text', 'date']].dropna()

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)  # remove URLs
    text = re.sub(r"[^a-z0-9@#\s]", "", text)  # keep words, @, #
    text = re.sub(r"\s+", " ", text).strip()
    return text

df['clean_text'] = df['text'].apply(clean_text)

def extract_mentions(text):
    mentions = re.findall(r"@([A-Za-z0-9_]+)", text)
    return mentions

df['mentions'] = df['clean_text'].apply(extract_mentions)

def extract_hashtags(text):
    return re.findall(r"#(\w+)", text)

df['hashtags'] = df['clean_text'].apply(extract_hashtags)

print(df[['user_name', 'clean_text', 'mentions', 'hashtags']].head(10))

df.to_csv("public/processed_data.csv", index=False)