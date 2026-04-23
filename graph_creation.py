import networkx as nx
from itertools import combinations
import ast
import pandas as pd
import pickle

with open("public/user_sentiment.pkl", "rb") as f:
    user_sentiment = pickle.load(f)

SENTIMENT_THRESHOLD = 0.7


df = pd.read_csv("public/processed_data.csv")

df['mentions'] = df['mentions'].apply(lambda x: ast.literal_eval(x))
df['hashtags'] = df['hashtags'].apply(lambda x: ast.literal_eval(x))

G = nx.Graph()

# Add nodes
for user in df['user_name']:
    G.add_node(user)

# -----------------------------
# Mention edges
# -----------------------------
for _, row in df.iterrows():
    user = row['user_name']
    for mention in row['mentions']:
        if user != mention:
            if G.has_edge(user, mention):
                G[user][mention]['weight'] += 1
            else:
                G.add_edge(user, mention, weight=1)

# -----------------------------
# Hashtag edges (with threshold)
# -----------------------------
MAX_USERS_PER_HASHTAG = 100

hashtag_map = {}

for _, row in df.iterrows():
    user = row['user_name']
    for tag in row['hashtags']:
        hashtag_map.setdefault(tag, []).append(user)

for tag, users in hashtag_map.items():
    if len(users) > MAX_USERS_PER_HASHTAG:
        continue

    for u1, u2 in combinations(users, 2):

        if u1 == u2:
            continue

        # skip if sentiment missing
        if u1 not in user_sentiment or u2 not in user_sentiment:
            continue

        # check sentiment similarity
        if abs(user_sentiment[u1] - user_sentiment[u2]) > SENTIMENT_THRESHOLD:
            continue

        # add edge
        if G.has_edge(u1, u2):
            G[u1][u2]['weight'] += 1
        else:
            G.add_edge(u1, u2, weight=1)

MIN_DEGREE = 2

nodes_to_remove = [n for n, d in G.degree() if d < MIN_DEGREE]
G.remove_nodes_from(nodes_to_remove)

print("After cleaning:")
print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())

largest_cc = max(nx.connected_components(G), key=len)
G = G.subgraph(largest_cc).copy()

print("Largest component:")
print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())

with open('public/graph.pkl', 'wb') as f:
   pickle.dump(G, f)