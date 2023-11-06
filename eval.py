
def read_paths(file_path):
    '''Reads all paths from the file'''
    
    with open(file_path) as f:
        content = f.readlines()
        # take every third line and convert to list
        # content = content[::3]
        # for new processed data, take every line
        all_paths = [x.strip().split(',') for x in content]
        # convert each node from ascii to number
        all_paths = [tuple([int(x) for x in path]) for path in all_paths]
    return all_paths

def get_paths_and_subpaths(src, dest, all_paths):
    '''Returns all paths and subpaths from src to dest'''
    
    paths = []
    for path in all_paths:
        if src in path and dest in path:
            src_index = path.index(src)
            dest_index = path.index(dest)
            if src_index < dest_index:
                paths.append(tuple(path[src_index:dest_index+1]))
    return paths

def f1_calculator(rec_paths, ground_paths):
    '''Calculates precision, recall and f1 score'''
    
    # precision
    # how much of the recommended path is in the ground paths
    # make a set of all nodes in the recommended path and ground paths
    # then intersection of the two sets
    rec_set = set(rec_paths)
    ground_set = set(ground_paths)
    intersection_set = rec_set.intersection(ground_set)
    precision = len(intersection_set) / len(rec_set)
    print('precision', precision)
    
    # recall
    # how much of the ground paths is in the recommended path
    # make a dictionary of all ground paths and their frequency
    ground_dict = {}
    for path in ground_paths:
        ground_dict[path] = ground_dict.get(path, 0) + 1
    print('ground_dict', ground_dict)
            
    # calculate the intersection as the sum of the frequency of common paths
    # use the intersection set from above
    intersection_freq = 0
    for path in intersection_set:
        intersection_freq += ground_dict.get(path, 0)
    
    # recall would be the intersection frequency divided by the 
    # total frequency of all the ground paths
    ground_total_freq = sum(ground_dict.values())
    recall = intersection_freq / ground_total_freq
    print('recall', recall)
    
    if precision + recall == 0:
        return 0
    f1 = 2 * precision * recall / (precision + recall)
    return f1

def get_f1_score(rec_path, relevant_paths):
    '''Returns f1 score'''

    rec_paths = [poi for poi in rec_path]
    relevant_paths = [poi for path in relevant_paths for poi in path]
    
    if len(relevant_paths) == 0:
        return 0
    return f1_calculator(rec_paths, relevant_paths)

def get_pairs_f1_score(rec_path, relevant_paths):
    '''Returns pairs-f1 score'''
    
    # first convert them to list of pairs
    convert = lambda path: [(path[i], path[i+1]) for i in range(len(path)-1)]
    rec_path_pairs = convert(rec_path)
    rel_paths_pairs = [convert(path) for path in relevant_paths] # list of list of pairs
    rel_paths_pairs = [item for sublist in rel_paths_pairs for item in sublist] # flatten

    if len(rel_paths_pairs) == 0:
        return 0
    return f1_calculator(rec_path_pairs, rel_paths_pairs)

# rec_path = (10, 11)
# all_paths = read_paths('processed_data/Edin.txt')
# relevant_paths = get_paths_and_subpaths(rec_path[0], rec_path[-1], all_paths)
# score_f1 = get_f1_score(rec_path, relevant_paths)
# print('score_f1', score_f1)
# score_pairs_f1 = get_pairs_f1_score(rec_path, relevant_paths)
# print('score_pairs_f1', score_pairs_f1)

__all__ = ['get_f1_score', 'get_pairs_f1_score', 'read_paths', 'get_paths_and_subpaths']