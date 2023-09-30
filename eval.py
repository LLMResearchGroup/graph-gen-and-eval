
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

def f1_calculator(rec_path, relevant_paths):
    '''Returns precision, recall and f1 score'''
    
    rel_path_dict = {}
    for path in relevant_paths:
        if path in rel_path_dict:
            rel_path_dict[path] += 1
        else:
            rel_path_dict[path] = 1
            
    print('rel_path_dict', rel_path_dict)
            
    # intersection
    intersection = 0
    for path in rec_path:
        if path in rel_path_dict:
            intersection += 1
            rel_path_dict[path] -= 1
            if rel_path_dict[path] == 0:
                del rel_path_dict[path]
    print('intersection', intersection)
    # precision
    precision = intersection / len(rec_path)
    print('precision', precision)
    # recall
    recall = intersection / len(relevant_paths)
    print('recall', recall)
    
    if precision + recall == 0:
        return 0
    f1 = 2 * precision * recall / (precision + recall)
    return f1

def get_f1_score(rec_path, relevant_paths):
    '''Returns f1 score'''
    
    if len(relevant_paths) == 0:
        return 0
    rec_paths = [rec_path]
    return f1_calculator(rec_paths, relevant_paths)

def get_pairs_f1_score(rec_path, relevant_paths):
    '''Returns pairs-f1 score'''
    
    # first convert them to list of pairs
    convert = lambda path: [(path[i], path[i+1]) for i in range(len(path)-1)]
    rec_path_pairs = convert(rec_path)
    rel_paths_pairs = [convert(path) for path in relevant_paths]
    rel_paths_pairs = [item for sublist in rel_paths_pairs for item in sublist]

    if len(rel_paths_pairs) == 0:
        return 0
    return f1_calculator(rec_path_pairs, rel_paths_pairs)

# rec_path = (10, 11)
# all_paths = read_paths('processed_data/Edin.txt')
# relevant_paths = get_paths_and_subpaths(rec_path[0], rec_path[-1], all_paths)
# score_f1 = get_f1_score(rec_path, relevant_paths)
# print(score_f1)
# score_pairs_f1 = get_pairs_f1_score(rec_path, relevant_paths)
# print(score_pairs_f1)

__all__ = ['get_f1_score', 'get_pairs_f1_score', 'read_paths', 'get_paths_and_subpaths']