import random
import openai
import os
import time
from dotenv import load_dotenv
from eval import *
from graph_gen import *

load_dotenv()
openai.api_key = os.getenv("OPENAI")

csv_file = open('eval_results.csv', 'w')
csv_file.write('n_nodes, n_edges, f1_score, pairs_f1_score\n')

n_nodes = [10, 12, 13, 17]
n_edges = [20, 25, 30, 40]

# n_nodes = [5]
# n_edges = [10]

for n_node, n_edge in zip(n_nodes, n_edges):
    curr_graph = generate_graph(n_node, n_edge)
    # print(describe_graph(curr_graph, GraphPrompt.Basic))

    prompt1 = describe_graph(curr_graph, GraphPrompt.Build_A_Graph) + '\n'
    path_freq = generate_randomly_distributed_path(curr_graph, n_edge*2)
    for path, freq in path_freq.items():
        prompt1 += 'path: ' + str(path) + ' freq: ' + str(freq) + '\n'
    
    src = random.randint(0, (n_node) // 2)
    dest = random.randint((n_node) // 2 + 1, n_node-1)
    prompt1 += 'From these historical paths, give me the most popular path from ' + str(src) + ' to ' + str(dest) + '\n'
    
    print(prompt1)

    response1 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        # temperature=0.7,
        messages=[
            {"role": "system", "content": "Think step by step."},
            {"role": "user", "content": prompt1},
        ],
    )
    
    print(response1.choices[0].message.content)
    
    time.sleep(1)
    
    prompt2 = 'The following text is a result for calculating popular path from ' + str(src) + ' to ' + str(dest) + '\n'
    prompt2 += 'Format the answer as a list of nodes, e.g. [1, 2, 3]\n'
    prompt2 += 'Do not include anything else in your answer\n'
    prompt2 += response1.choices[0].message.content + '\n'
    print(prompt2)
    
    response2 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        # temperature=0.7,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt2},
        ],
    )
    
    print(response2.choices[0].message.content)
    
    rec_path = eval(response2.choices[0].message.content)   
    all_paths = [list(path) for path in path_freq.keys()]
    paths = get_paths_and_subpaths(rec_path[0], rec_path[-1], all_paths)
    score_f1 = get_f1_score(rec_path, paths)
    score_pairs_f1 = get_pairs_f1_score(rec_path, paths)
    print(f'f1 score: {score_f1}, pairs f1 score: {score_pairs_f1}')
    csv_file.write(f'{n_node}, {n_edge}, {score_f1}, {score_pairs_f1}\n')