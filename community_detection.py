import networkx as nx
import pickle


with open('public/graph.pkl', 'rb') as f:
    G= pickle.load(f)


import community as community_louvain

print("Running Louvain...")

partition = community_louvain.best_partition(G)

print("Total communities:", len(set(partition.values())))

# Save communities
with open("public/communities.pkl", "wb") as f:
    pickle.dump(partition, f)

# Sample output
print(list(partition.items())[:10])