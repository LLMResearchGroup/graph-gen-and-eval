import csv

def process_data(region):
    # userID,trajID,poiID,startTime,endTime,#photo,trajLen,poiDuration
    with open(f'dataset/traj-{region}.csv') as f:
        csv_reader = csv.DictReader(f)
        
        # take a dict of all the trajectories
        # key: trajectory id
        # value: list of nodes/pois
        trajectories = {}
        for row in csv_reader:
            # ignore trajectories with length smaller than 3
            if int(row['trajLen']) < 3:
                continue
            # keep them in ascii, no need to convert to int now
            trajID = row['trajID']
            poiID = row['poiID']
            startTime = row['startTime']
            if trajID not in trajectories:
                trajectories[trajID] = []
            trajectories[trajID].append((poiID, startTime))
            
        # now sort the trajectories by the start time
        for k, v in trajectories.items():
            trajectories[k] = sorted(v, key=lambda x: x[1])
                
    trajectories = {k: [x[0] for x in v] for k, v in trajectories.items()}
            
    with open(f'processed_data/{region}.txt', 'w') as f:
        for traj in trajectories.values():
            f.write(','.join(traj) + '\n')
            
regions = ['caliAdv', 'disHolly', 'disland', 'Edin', 'epcot', 'Glas', 'MagicK', 'Melb', 'Osak', 'Toro']
for region in regions:
    process_data(region)