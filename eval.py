
def read_paths(file_path):
    '''Reads all paths from the file'''
    with open(file_path) as f:
        content = f.readlines()
        # take every third line and convert to list
        # content = content[::3]
        # for new processed data, take every line
        all_paths = [x.strip().split(',') for x in content]
        # convert each node from ascii to number
        all_paths = [[int(x) for x in path] for path in all_paths]
    return all_paths

def get_paths_and_subpaths(src, dest, all_paths):
    '''Returns all paths and subpaths from src to dest'''
    paths = []
    for path in all_paths:
        if src in path and dest in path:
            src_index = path.index(src)
            dest_index = path.index(dest)
            if src_index < dest_index:
                paths.append(path[src_index:dest_index+1])
    return paths

def f1_calculator(rec_path_set, paths_set):
    '''Returns precision, recall and f1 score'''
    precision = len(rec_path_set.intersection(paths_set)) / len(rec_path_set)
    recall = len(rec_path_set.intersection(paths_set)) / len(paths_set)
    if precision + recall == 0:
        return 0
    f1 = 2 * precision * recall / (precision + recall)
    return f1

def get_f1_score(rec_path, paths):
    '''Returns f1 score'''
    if len(paths) == 0:
        return 0
    # first convert them to set of tuples
    rec_path_set = set([tuple(rec_path)])
    paths_set = set([tuple(path) for path in paths])
    return f1_calculator(rec_path_set, paths_set)

def get_pairs_f1_score(rec_path, paths):
    '''Returns pairs-f1 score'''
    # first convert them to list of pairs
    convert = lambda path: [(path[i], path[i+1]) for i in range(len(path)-1)]
    rec_path_pairs = convert(rec_path)
    paths_pairs = [convert(path) for path in paths]
    paths_pairs = [item for sublist in paths_pairs for item in sublist]

    if len(paths_pairs) == 0:
        return 0
    # first convert them to set of tuples
    rec_path_set = set(rec_path_pairs)
    paths_set = set(paths_pairs)
    return f1_calculator(rec_path_set, paths_set)

# rec_path = [10, 11]
# all_paths = read_paths('processed_data/Edin.txt')
# paths = get_paths_and_subpaths(rec_path[0], rec_path[-1], all_paths)
# score_f1 = get_f1_score(rec_path, paths)
# print(score_f1)
# score_pairs_f1 = get_pairs_f1_score(rec_path, paths)
# print(score_pairs_f1)

__all__ = ['get_f1_score', 'get_pairs_f1_score', 'read_paths', 'get_paths_and_subpaths']