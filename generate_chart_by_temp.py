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
cursor = collection.find({"node_number": {"$gte": 5}, "path_number": {"$gte": 5}, "date": {"$gte": "2023-11-07 09:00:00"}},
                         {"temperature": 1, "f1_score": 1, "f1_pair_score": 1, "_id": 0})

# Iterate through the documents and populate the data list
for doc in cursor:
    data.append(doc)
    
# Create a DataFrame from the data
df = pd.DataFrame(data)

# Group the data by "node_number" and calculate the average scores
avg_scores = df.groupby("temperature")[["f1_score", "f1_pair_score"]].mean()

# Create a bar chart for the average scores
plt.figure(figsize=(10, 6))
avg_scores.plot(kind="bar")
plt.xlabel("Temperature")
plt.ylabel("Average Scores")
plt.title("Average Scores for Each Temperature")
plt.legend(["f1_score", "f1_pair_score"])
plt.grid(True)
chart_filename = "generated_results/average_scores_by_temp.png"
plt.savefig(chart_filename)
plt.close()

print("Average scores bar chart for each temperature generated successfully.")
