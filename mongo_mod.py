from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

def insert_json_to_mongodb(json_data, mongodb_uri, database_name, collection_name):
    # Connect to MongoDB server
    client = MongoClient(mongodb_uri, server_api=ServerApi('1'))

    # Get database and collection
    db = client[database_name]
    collection = db[collection_name]

    try:
        # Insert data into collection
        collection.insert_one(json_data)
    except Exception as e:
        print("Error inserting data into MongoDB: {0}".format(e))

    # Close connection
    client.close()


data = {
    "node_number": 10,
    "edge_number": 20,
    "path_number": 5,
    "trajectory_list": [
        {"path": [1, 2, 3], "freq": 10},
        {"path": [4, 5, 6], "freq": 5},
        {"path": [7, 8, 9], "freq": 3},
        {"path": [1, 2, 3, 4, 5], "freq": 2},
        {"path": [6, 7, 8, 9], "freq": 1},
    ],
    "graph_description": "This is a sample graph",
    "source": 1,
    "destination": 6,
    "prompt1": "What is your name?",
    "prompt2": "How old are you?",
    "response1": "My name is John",
    "response2": [25, 30, 35],
    "f1_score": 0.85,
    "f1_pair_score": 0.75
}
# temperature
# chatgpt version

load_dotenv()
uri = os.getenv("MONGOURI")
insert_json_to_mongodb(data, uri, "DemoGraph", "Alpha")