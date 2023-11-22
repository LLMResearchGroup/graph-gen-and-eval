import pymongo
import pandas as pd
import matplotlib.pyplot as plt 
from dotenv import load_dotenv
import os
import numpy as np

load_dotenv()
uri = os.getenv("MONGOURI")

# Connect to your MongoDB database
client = pymongo.MongoClient(uri)
db = client["DemoGraph"]
collection = db["Alpha"]

# Create an empty DataFrame to store the data
data = []

# Query the collection to retrieve the necessary fields
cursor = collection.find({"date": {"$gte": "2023-11-20 22:00:00"}}, {"node_number": 1, "edge_number": 1, "path_number": 1, "f1_score": 1, "f1_pair_score": 1, "_id": 0})

# Iterate through the documents and populate the data list
for doc in cursor:
    data.append(doc)
    
# Create a DataFrame from the data
df = pd.DataFrame(data)

# Create a bar graph of increasing graph size with fixed number of paths
# as the number of paths may vary slightly, take a range of paths and calculate the average scores against the range of paths
# First group by range of paths
min = 0
max = 100
gap = 10
bins = np.arange(min, max, gap)
df['path_number_range'] = pd.cut(df['path_number'], bins=bins, labels=[f"{i}-{i+gap-1}" for i in range(min, max-gap, gap)])

grouped = df.groupby("path_number_range")

for path_number, group_data in grouped:
    # calculate the average scores
    group_data = group_data.sort_values(by="node_number")
    avg_scores = group_data.groupby(["node_number", "edge_number"])[["f1_score", "f1_pair_score"]].mean()
    # create a bar chart for the average scores
    plt.figure(figsize=(10, 8))
    avg_scores.plot(kind="bar")
    plt.xlabel("Graph Size")
    plt.ylabel("Average Scores")
    plt.title(f"Number of Paths: {path_number}")
    plt.savefig(f"by_size/paths_{path_number}.png")
    plt.close()
