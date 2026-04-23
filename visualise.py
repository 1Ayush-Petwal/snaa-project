import os
import pickle
import networkx as nx
import plotly.graph_objects as go

# -----------------------------
# CONFIG
# -----------------------------
GRAPH_PATH = "public/graph.pkl"
COMMUNITIES_PATH = "public/communities.pkl"
LAYOUT_CACHE_PATH = "public/layout.pkl"

EDGE_WEIGHT_THRESHOLD = 2      # drop weak edges
MIN_DEGREE = 2                 # drop weakly-connected nodes after filtering
MAX_NODES = 3000               # cap nodes to keep layout/render light
LAYOUT_ITERATIONS = 15         # fewer iterations = much faster spring layout
LAYOUT_SEED = 42

# -----------------------------
# LOAD GRAPH + COMMUNITIES
# -----------------------------
with open(GRAPH_PATH, "rb") as f:
    G = pickle.load(f)

with open(COMMUNITIES_PATH, "rb") as f:
    partition = pickle.load(f)

print("Original nodes:", G.number_of_nodes())
print("Original edges:", G.number_of_edges())

# -----------------------------
# FILTER WEAK EDGES
# -----------------------------
edges = [(u, v) for u, v, d in G.edges(data=True)
        if d.get("weight", 1) >= EDGE_WEIGHT_THRESHOLD]

G_vis = nx.Graph()
G_vis.add_edges_from(edges)

# Drop low-degree nodes to shrink the layout problem
low_deg = [n for n, d in G_vis.degree() if d < MIN_DEGREE]
G_vis.remove_nodes_from(low_deg)

# Cap to top-N highest-degree nodes so layout stays cheap on a laptop
if G_vis.number_of_nodes() > MAX_NODES:
    top_nodes = sorted(G_vis.degree, key=lambda x: x[1], reverse=True)[:MAX_NODES]
    keep = {n for n, _ in top_nodes}
    G_vis = G_vis.subgraph(keep).copy()

print("Filtered nodes:", G_vis.number_of_nodes())
print("Filtered edges:", G_vis.number_of_edges())

# -----------------------------
# LAYOUT (cached)
# -----------------------------
layout_key = (G_vis.number_of_nodes(), G_vis.number_of_edges(),
              EDGE_WEIGHT_THRESHOLD, MIN_DEGREE, MAX_NODES, LAYOUT_ITERATIONS)

pos = None
if os.path.exists(LAYOUT_CACHE_PATH):
    try:
        with open(LAYOUT_CACHE_PATH, "rb") as f:
            cached = pickle.load(f)
        if cached.get("key") == layout_key and set(cached["pos"].keys()) == set(G_vis.nodes()):
            pos = cached["pos"]
            print("Loaded cached layout.")
    except Exception:
        pos = None

if pos is None:
    print(f"Computing layout ({LAYOUT_ITERATIONS} iterations)...")
    pos = nx.spring_layout(
        G_vis,
        k=0.15,
        iterations=LAYOUT_ITERATIONS,
        seed=LAYOUT_SEED,
    )
    with open(LAYOUT_CACHE_PATH, "wb") as f:
        pickle.dump({"key": layout_key, "pos": pos}, f)

# -----------------------------
# EDGE TRACE (WebGL)
# -----------------------------
edge_x = []
edge_y = []
for u, v in G_vis.edges():
    x0, y0 = pos[u]
    x1, y1 = pos[v]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])

edge_trace = go.Scattergl(
    x=edge_x,
    y=edge_y,
    line=dict(width=0.2, color="#888"),
    hoverinfo="none",
    mode="lines",
)

# -----------------------------
# NODE TRACE (WebGL)
# -----------------------------
node_x = []
node_y = []
node_color = []
node_text = []

for node in G_vis.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    comm = partition.get(node, -1)
    node_color.append(comm)
    node_text.append(f"{node}<br>Community: {comm}")

node_trace = go.Scattergl(
    x=node_x,
    y=node_y,
    mode="markers",
    hoverinfo="text",
    text=node_text,
    marker=dict(
        size=4,
        color=node_color,
        colorscale="Viridis",
        showscale=True,
        colorbar=dict(title="Community"),
    ),
)

# -----------------------------
# PLOT
# -----------------------------
fig = go.Figure(data=[edge_trace, node_trace])
fig.update_layout(
    title="Graph Visualization (Community Colored)",
    showlegend=False,
    hovermode="closest",
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
)

fig.show()
