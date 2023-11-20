import random, openai, os, time, json, datetime
from dotenv import load_dotenv
from eval import *
from graph_gen import *
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from mongo import insert_json_to_mongodb

# evaluation parameters
# n_nodes = [5, 7, 10, 12, 15]
# n_edges = [7, 12, 17, 20, 25]
n_nodes = [15,20,25]
n_edges = [30,40,50]
temperatures = [0.1, 0.3, 0.5, 0.7, 0.9]
n_paths = [40, 45, 50, 55, 60]
chatgpt_version = "gpt-3.5-turbo-1106"
n_iter = 1  # number of iterations for each graph

# necessary initialization
load_dotenv()
openai.api_key = os.getenv("OPENAI")
log_file = open("log.txt", "a")
# create csv file if doesn't exist and write header
# open in append mode if exists
if not os.path.exists("eval_results.csv"):
    csv_file = open("eval_results.csv", "w")
    csv_file.write("n_nodes, n_edges, n_paths, temperature, f1_score, f1_pair_score\n")
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
    pair = (random.randint(0, number_of_nodes-1), random.randint(0, number_of_nodes-1))
    while pair[0] == pair[1]:
        pair = (random.randint(0, number_of_nodes-1), random.randint(0, number_of_nodes-1))
    return pair

for n_node, n_edge in zip(n_nodes, n_edges):
    for temperature in temperatures:
        for n_path in n_paths:
            for iter1 in range(n_iter):
                log_file.write("----------------------------------------\n")
                log_file.write("Starting new evaluation\n")
                log_file.write("n_node: " + str(n_node) + "\n")
                log_file.write("n_edge: " + str(n_edge) + "\n")
                log_file.write("n_path: " + str(n_path) + "\n")
                log_file.write("temperature: " + str(temperature) + "\n")
                log_file.write("chatgpt_version: " + str(chatgpt_version) + "\n")
                log_file.write("iter: " + str(iter1) + "\n")
                
                # generate graph and paths
                graph = generate_graph(n_node, n_edge)
                evaluation_prompt = describe_graph(graph, GraphPrompt.Build_A_Graph) + "\n"
                evaluation_prompt += "Now, I will give you some historical paths.\n"
                path_freq = generate_randomly_distributed_path(
                    graph, n_path, ProbabilityDistribution.Normal
                )
                for path, freq in path_freq.items():
                    evaluation_prompt += "path: " + str(path) + " freq: " + str(freq) + "\n"
                
                    
                for iter2 in range(n_iter):
                    src, dest = generate_node_pair(n_node)
                    evaluation_prompt += (
                        "From these historical paths, give me the most popular path from " + str(src) + " to " + str(dest) + "\n"
                    )
                    evaluation_prompt += "You must give an answer in the following format:\n"
                    evaluation_prompt += "(1, 2, 3)\n"
                    evaluation_prompt += "Not giving an answer is not allowed, multiple answer is also not allowed\n"
                    evaluation_prompt += "You must give one and only one answer\n"
                    print("***Evaluation prompt:")
                    print(evaluation_prompt)
                    log_file.write("Evaluation prompt:\n")
                    log_file.write(evaluation_prompt)
                    log_file.write("\n")

                    try:
                        evaluation_response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo-1106",
                            temperature=temperature,
                            messages=[
                                {"role": "system", "content": "Think step by step."},
                                {"role": "user", "content": evaluation_prompt},
                            ],
                        )
                    except Exception as e:
                        print("Error in chat completion", e)
                        log_file.write("Error in chat completion\n")
                        log_file.write(str(e)+"\n")
                        continue
                            
                    # print(evaluation_response)
                    evaluation_response = evaluation_response.choices[0].message.content
                    print("***Evaluation response:")
                    print(evaluation_response)
                    log_file.write("Evaluation response:\n")
                    log_file.write(evaluation_response)
                    log_file.write("\n")

                    # wait for half second to avoid rate limit
                    # time.sleep(0.5)

                    format_prompt = (
                        "The following text is a result for calculating popular path from " + str(src) + " to " + str(dest) + "\n"
                    )
                    format_prompt += "Format the answer as a list of nodes, e.g. (1, 2, 3)\n"
                    format_prompt += "Do not include anything else in your answer\n"
                    log_file.write("Formatting prompt:\n")
                    log_file.write(format_prompt)
                    log_file.write("\n")
                    format_prompt += "Answer starts here:\n"
                    format_prompt += evaluation_response + "\n"
                    format_prompt += "Answer ends here\n"

                    try:
                        format_response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo-1106",
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant."},
                                {"role": "user", "content": format_prompt},
                            ],
                        )
                    except Exception as e:
                        print("Error in chat completion", e)
                        log_file.write("Error in chat completion\n")
                        log_file.write(str(e)+"\n")
                        continue
                    
                    format_response = format_response.choices[0].message.content
                    log_file.write("Formatting response:\n")
                    log_file.write(format_response)
                    log_file.write("\n")

                    # wait for half second to avoid rate limit
                    # time.sleep(0.5)

                    # evaluate the response
                    try :
                        rec_path = eval(format_response)
                                
                    except Exception as e:
                        print("Invalid answer format", e)
                        log_file.write("Invalid answer format\n")
                        log_file.write(str(e)+"\n")
                        continue
                    
                    all_paths = [path for path, freq in path_freq.items() for _ in range(freq)]
                    paths = get_paths_and_subpaths(rec_path[0], rec_path[-1], all_paths)
                    score_f1 = get_f1_score(rec_path, paths)
                    score_pairs_f1 = get_pairs_f1_score(rec_path, paths)
                    print("***Evaluation result:")
                    print(f"n_node: {n_node}, n_edge: {n_edge}, n_path: {n_path}, temperature: {temperature}, f1 score: {score_f1}, pairs f1 score: {score_pairs_f1}")
                    csv_file.write(f"{n_node}, {n_edge}, {n_path}, {temperature}, {score_f1}, {score_pairs_f1}\n")
                    log_file.write(f"f1 score: {score_f1}, pairs f1 score: {score_pairs_f1}\n")
                    log_file.write("----------------------------------------\n")
                    
                    json_data = {
                        "node_number": n_node,
                        "edge_number": n_edge,
                        "path_number": len(path_freq),
                        # we don't control path length yet
                        "avg_path_length": sum([len(path) for path in path_freq.keys()]) / len(path_freq) if len(path_freq) > 0 else -1,
                        "temperature": temperature,
                        "version": chatgpt_version,
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "freq_distribution": "Normal",
                        "trajectory_list": [
                            {"path": path, "freq": freq} for path, freq in path_freq.items()
                        ],
                        "graph_description": describe_graph(graph, GraphPrompt.Build_A_Graph),
                        "source": src,
                        "destination": dest,
                        "prompt1": evaluation_prompt,
                        "prompt2": format_prompt,
                        "response1": evaluation_response,
                        "response2": format_response,
                        "f1_score": score_f1,
                        "f1_pair_score": score_pairs_f1,
                    }
                    json_file.write(json.dumps(json_data))
                    json_file.write("\n")
                    
                    insert_json_to_mongodb(json_data)
                
log_file.close()
csv_file.close()
json_file.close()