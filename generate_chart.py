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
cursor = collection.find({"node_number": {"$gte": 5}, "date": {"$gte": "2023-11-20 22:00:00"}},
                         {"node_number": 1, "edge_number": 1, "path_number": 1, "f1_score": 1, "f1_pair_score": 1, "_id": 0})

# Print number of documents retrieved
# print(cursor.count(), "documents retrieved.")

# Iterate through the documents and populate the data list
for doc in cursor:
    data.append(doc)

# Create a DataFrame from the data
df = pd.DataFrame(data)

# Group the data by "node_number" and "edge_number"
grouped = df.groupby(["node_number", "edge_number"])

# Iterate through the grouped data and create CSV files and graphs for each combination
for (node_number, edge_number), group_data in grouped:
    # filename = f"generated_results/node_{node_number}_edge_{edge_number}_data.csv"
    # group_data.to_csv(filename, index=False)

    # Create a bar graph "f1_score" and "f1_pair_score" with "path_number" on the x-axis
    # sort in ascending path number
    group_data = group_data.sort_values(by="path_number")
    # create ranges of 5
    min_path_number = group_data["path_number"].min()
    max_path_number = group_data["path_number"].max()
    gap = (max_path_number - min_path_number)//4
    bins = np.arange(min_path_number, max_path_number + gap, gap)
    # create a new column in the DataFrame that specifies the bin for each path number
    group_data["path_number_range"] = pd.cut(group_data["path_number"], bins=bins, labels=[f"{i}-{i+gap-1}" for i in range(min_path_number, max_path_number, gap)])
    # group the data by path number range and calculate the average scores
    avg_scores = group_data.groupby("path_number_range")[["f1_score", "f1_pair_score"]].mean()

    # avg_scores = group_data.groupby("path_number")[["f1_score", "f1_pair_score"]].mean()

    # create a bar chart for the average scores
    plt.figure(figsize=(10, 8))
    avg_scores.plot(kind="bar")
    plt.xlabel("Path Number")
    plt.ylabel("Average Scores")
    plt.title(f"Node: {node_number}, Edge: {edge_number}")
    plt.legend(["f1_score", "f1_pair_score"])
    plt.grid(True)
    chart_filename = f"generated_results/node_{node_number}_edge_{edge_number}_scores.png"
    plt.savefig(chart_filename)
    plt.close()

print("CSV files and dot plots created.")

# Define the bins for path numbers
min_path_number = df["path_number"].min()
max_path_number = df["path_number"].max()
print(min_path_number, max_path_number)
bins = np.arange(min_path_number, max_path_number + 20, 20)

# Create a new column in the DataFrame that specifies the bin for each path number
df["path_number_range"] = pd.cut(df["path_number"], bins=bins, labels=[f"{i}-{i+19}" for i in range(min_path_number, max_path_number, 20)])

# Group the data by path number range and calculate the average scores
avg_scores = df.groupby("path_number_range")[["f1_score", "f1_pair_score"]].mean()

# avg_scores = df.groupby("path_number")[["f1_score", "f1_pair_score"]].mean()

# Create a bar chart for the average scores
plt.figure(figsize=(10, 8))
avg_scores.plot(kind="bar")
plt.xlabel("Path Number")
plt.ylabel("Average Scores")
plt.title("Average Scores for Each Path Number Range")
plt.legend(["f1_score", "f1_pair_score"])
plt.grid(True)
chart_filename = "generated_results/average_scores.png"
plt.savefig(chart_filename)
plt.close()

print("Average scores graph created.")