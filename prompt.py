import random
import openai
import os
import time
import json
from dotenv import load_dotenv
from eval import *
from graph_gen import *
import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# evaluation parameters
# n_nodes = [10, 15, 20]
# n_edges = [20, 30, 40]
n_nodes = [5]
n_edges = [7]
evaluation_ratio = 2  # number of paths generated for each edge
temperature = 0.2 # temperature for the model
chatgpt_version = "gpt-3.5-turbo_unspecified_version"

# necessary initialization
load_dotenv()
openai.api_key = os.getenv("OPENAI")
log_file = open("log.txt", "a")
# create csv file if doesn't exist and write header
# open in append mode if exists
if not os.path.exists("eval_results.csv"):
    csv_file = open("eval_results.csv", "w")
    csv_file.write("n_nodes, n_edges, f1_score, pairs_f1_score\n")
else:
    csv_file = open("eval_results.csv", "a")
json_file = open("log.json", "a")


# utility functions
def generate_node_pair(number_of_nodes: int) -> tuple:
    # Type validity
    if not isinstance(number_of_nodes, int):
        raise TypeError("number_of_nodes must be an int")

    # Check if the number of nodes is valid
    if number_of_nodes < 2:
        raise ValueError("number_of_nodes must be larger than 1")

    # Generate random node pairs
    pair = (random.randint(0, number_of_nodes), random.randint(0, number_of_nodes))
    while pair[0] == pair[1]:
        pair = (random.randint(0, number_of_nodes), random.randint(0, number_of_nodes))
    return pair

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

for n_node, n_edge in zip(n_nodes, n_edges):
    graph = generate_graph(n_node, n_edge)
    evaluation_prompt = describe_graph(graph, GraphPrompt.Build_A_Graph) + "\n"
    evaluation_prompt += "Now, I will give you some historical paths.\n"
    path_freq = generate_randomly_distributed_path(
        graph, n_edge * evaluation_ratio, ProbabilityDistribution.Normal
    )
    for path, freq in path_freq.items():
        evaluation_prompt += "path: " + str(path) + " freq: " + str(freq) + "\n"
    src, dest = generate_node_pair(n_node)
    evaluation_prompt += (
        "From these historical paths, give me the most popular path from "
        + str(src)
        + " to "
        + str(dest)
        + "\n"
    )
    evaluation_prompt += "You must give an answer in the following format:\n"
    evaluation_prompt += "(1, 2, 3)\n"
    evaluation_prompt += "Not giving an answer is not allowed, multiple answer is also not allowed\n"
    evaluation_prompt += "You must give one and only one answer\n"
    print(evaluation_prompt)
    log_file.write("----------------------------------------\n")
    log_file.write("Starting new evaluation\n")
    log_file.write("Evaluation prompt:\n")
    log_file.write(evaluation_prompt)
    log_file.write("\n")

    evaluation_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=temperature,
        messages=[
            {"role": "system", "content": "Think step by step."},
            {"role": "user", "content": evaluation_prompt},
        ],
    )
    # print(evaluation_response)
    print(evaluation_response.choices[0].message.content)
    log_file.write("Evaluation response:\n")
    log_file.write(evaluation_response.choices[0].message.content)
    log_file.write("\n")

    # wait for 1 second to avoid rate limit
    time.sleep(1)

    format_prompt = (
        "The following text is a result for calculating popular path from "
        + str(src)
        + " to "
        + str(dest)
        + "\n"
    )
    format_prompt += "Format the answer as a list of nodes, e.g. (1, 2, 3)\n"
    format_prompt += "Do not include anything else in your answer\n"
    log_file.write("Formatting prompt:\n")
    log_file.write(format_prompt)
    log_file.write("\n")
    format_prompt += "Answer starts here:\n"
    format_prompt += evaluation_response.choices[0].message.content + "\n"
    format_prompt += "Answer ends here\n"
    print(format_prompt)

    format_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": format_prompt},
        ],
    )
    print(format_response.choices[0].message.content)
    log_file.write("Formatting response:\n")
    log_file.write(format_response.choices[0].message.content)
    log_file.write("\n")

    # wait for 1 second to avoid rate limit
    time.sleep(1)

    # evaluate the response
    format_response = format_response.choices[0].message.content
    try :
        rec_path = eval(format_response)
        all_paths = [path for path, freq in path_freq.items() for _ in range(freq)]
        paths = get_paths_and_subpaths(rec_path[0], rec_path[-1], all_paths)
        score_f1 = get_f1_score(rec_path, paths)
        score_pairs_f1 = get_pairs_f1_score(rec_path, paths)
        print(f"f1 score: {score_f1}, pairs f1 score: {score_pairs_f1}")
        csv_file.write(f"{n_node}, {n_edge}, {score_f1}, {score_pairs_f1}\n")
        log_file.write(f"f1 score: {score_f1}, pairs f1 score: {score_pairs_f1}\n")
        log_file.write("----------------------------------------\n")
        
        json_data = {
            "node_number": n_node,
            "edge_number": n_edge,
            "path_number": len(path_freq),
            "temperature": temperature,
            "version": chatgpt_version,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "trajectory_list": [
                {"path": path, "freq": freq} for path, freq in path_freq.items()
            ],
            "graph_description": describe_graph(graph, GraphPrompt.Build_A_Graph),
            "source": src,
            "destination": dest,
            "prompt1": evaluation_prompt,
            "prompt2": format_prompt,
            "response1": evaluation_response.choices[0].message.content,
            "response2": format_response.choices[0].message.content,
            "f1_score": score_f1,
            "f1_pair_score": score_pairs_f1,
        }
        json_file.write(json_data)
        
        load_dotenv()
        uri = os.getenv("MONGOURI")
        insert_json_to_mongodb(json_data, uri, "DemoGraph", "Alpha")
        
    except Exception as e:
        print("Invalid answer format")
        print(e)
        log_file.write("Invalid answer format\n")
        continue
        
log_file.close()
csv_file.close()
json_file.close()