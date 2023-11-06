import pymongo
import pandas as pd
import matplotlib.pyplot as plt 
from dotenv import load_dotenv
import os

load_dotenv()
uri = os.getenv("MONGOURI")

# Connect to your MongoDB database
client = pymongo.MongoClient(uri)
db = client["DemoGraph"]
collection = db["Alpha"]

# Create an empty DataFrame to store the data
data = []

# Query the collection to retrieve the necessary fields
cursor = collection.find({}, {"node_number": 1, "edge_number": 1, "path_number": 1, "f1_score": 1, "f1_pair_score": 1, "_id": 0})

# Iterate through the documents and populate the data list
for doc in cursor:
    data.append(doc)

# Create a DataFrame from the data
df = pd.DataFrame(data)

# Group the data by "node_number" and "edge_number"
grouped = df.groupby(["node_number", "edge_number"])

# Iterate through the grouped data and create CSV files and graphs for each combination
for (node_number, edge_number), group_data in grouped:
    filename = f"node_{node_number}_edge_{edge_number}_data.csv"
    group_data.to_csv(filename, index=False)

    # Create a dot plot for "f1_score" and "f1_pair_score" with "path_number" on the x-axis
    plt.figure(figsize=(10, 6))
    plt.plot(group_data["path_number"], group_data["f1_score"], 'o', label="f1_score")
    plt.plot(group_data["path_number"], group_data["f1_pair_score"], 'x', label="f1_pair_score")
    plt.xlabel("Path Number")
    plt.ylabel("Scores")
    plt.title(f"Node {node_number}, Edge {edge_number} - Scores")
    plt.legend()
    plt.grid(True)
    chart_filename = f"node_{node_number}_edge_{edge_number}_scores.png"
    plt.savefig(chart_filename)
    plt.close()

print("CSV files and dot plots created.")

# Group the data by "node_number" and calculate the average scores
avg_scores = df.groupby("node_number")[["f1_score", "f1_pair_score"]].mean()

# Create a bar chart for the average scores
plt.figure(figsize=(10, 6))
avg_scores.plot(kind="bar")
plt.xlabel("Node Number")
plt.ylabel("Average Scores")
plt.title("Average Scores for Each Node")
plt.legend(["f1_score", "f1_pair_score"])
plt.grid(True)
chart_filename = "average_scores.png"
plt.savefig(chart_filename)
plt.close()

print("Average scores graph created.")