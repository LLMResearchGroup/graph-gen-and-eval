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
cursor = collection.find({}, {"path_number": 1, "f1_score": 1, "f1_pair_score": 1, "_id": 0})

# Iterate through the documents and populate the data list
for doc in cursor:
    data.append(doc)
    
# Create a DataFrame from the data
df = pd.DataFrame(data)

# Create a bar graph "f1_score" and "f1_pair_score" with "path_number" on the x-axis
# sort in ascending path number
df = df.sort_values(by="path_number")
# create ranges of 5
min_path_number = df["path_number"].min()
max_path_number = df["path_number"].max()
bins = np.arange(min_path_number, max_path_number + 5, 5)
# create a new column in the DataFrame that specifies the bin for each path number
df["path_number_range"] = pd.cut(df["path_number"], bins=bins, labels=[f"{i}-{i+4}" for i in range(min_path_number, max_path_number, 5)])
# group the data by path number range and calculate the average scores
avg_scores = df.groupby("path_number_range")[["f1_score", "f1_pair_score"]].mean()
# create a bar chart for the average scores
plt.figure(figsize=(10, 6))
avg_scores.plot(kind="bar")
plt.xlabel("Path Number")
plt.ylabel("Average Scores")
plt.title("Average Scores for Each Path Number")
plt.legend(["f1_score", "f1_pair_score"])
plt.grid(True)
chart_filename = "generated_results/average_scores_by_path.png"
plt.savefig(chart_filename)
plt.close()

print("Average scores bar chart created.")