#import requests
import formulas
import csv

def get_focal_point(location_list, r1):
    
    # get lat and long for each address
    '''
    for address in address_list:
        response = requests.get("http://dev.virtualearth.net/REST/v1/Locations/" + address,
                            params={"include":"queryParse",
                            "key":"AvQOaBs2cYn6OAWmZ9tEAvGuJGfJusGnLSyHnD9g7USe35x69PmSiyk_51Htk3Z0"})
        data = response.json()
        lat = data['resourceSets'][0]['resources'][0]['point']['coordinates'][0]
        lng = data['resourceSets'][0]['resources'][0]['point']['coordinates'][1]
        
        # add to location_list
        location_list.append(address, lat, lng)

        print(str(lat) + ", " + str(lng))
    '''
    #list of location set around every point in tuple form (location, set)
    local_set_list =[]
    # iterate through location_list to create sets for each location
    for location in location_list:
        lat1 = location[0]
        lon1 = location[1]
        local_set = set()
        for other_location in location_list:
            lat2 = other_location[0]
            lon2 = other_location[1]
            dist = formulas.haversine(lat1, lon1, lat2, lon2)
            if dist <= r1:
                local_set.add(other_location)
        local_set_list.append((location, local_set))
    
    #local set around focal point of locations in (address, lat, long)
    local_set = None
    # focal point
    focal_point = None
    #iterate through dictionary to get largest set and focal point
    for loc, self_set in local_set_list:
        if (len(self_set) > len(local_set)):
            local_set = self_set
            focal_point = loc
    
    return (focal_point, local_set)

def create_remote_set(focal_point, location_list, r2):
    #remote set around focal point of locations in (address, lat, long)
    remote_set = None

    lat1 = focal_point[0]
    lon1 = focal_point[1]
    for loc in location_list:
        lat2 = loc[0]
        lon2 = loc[1]
        dist = formulas.haversine(lat1, lon1, lat2, lon2)
        if dist > r2:
            remote_set.add(loc)
    return remote_set


if __name__ == '__main__':
    ungrouped = set()
    r1 = 0
    r2 = 0
    with open('inputs/input.tsv', encoding='latin-1') as tsvfile:
        reader = csv.DictReader(tsvfile, dialect='excel-tab')
        
        #create the set of ungrouped addresses
        for row in reader:
            lat = row['lat']
            lng = row['lng']
            
            ungrouped.add((lat, lng))
            
    with open('inputs/arguments.tsv', encoding='latin-1') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        
        #create the set of ungrouped addresses
        for row in reader:
            r1 = row['r1']
            r2 = row['r2']
    
    #get the local locations
    (local_center, local_set) = get_focal_point(list(ungrouped), r1)
    #get the remote locations
    remote_set = create_remote_set(local_center, list(ungrouped), r2)
    #find the locations that are not local and not remote
    inbetween = ungrouped - remote_set - local_set
    
    #set of sets of remote groups
    remote_groups = set()
    
    while len(remote_set) > 0:
        #get largest remote group, add to remote groups and remove from set of ungrouped remotes
        remote_group = get_focal_point(remote_set, r1)
        remote_groups.add(remote_group)
        remote_set -= remote_group
       
    with open('outputs/groupings.tsv', 'w', newline="\n", encoding='latin-1') as out_file: 
        csv_writer = csv.writer(out_file, dialect='excel-tab')
        header = ["group_classification", "locations", "point_lat", "point_lng", "geographical_relationship"]
        csv_writer.writerow(header)
        
    csv_writer.writerow(['local', '; '.join(local_set), local_center[0], local_center[1], 'domestic'])
    csv_writer.writerow(['non-local', '; '.join(inbetween), 'N/A', 'N/A', 'N/A'])
    
    for remote_group in remote_groups:
        (coordinates, group) = remote_group
        csv_writer.writerow(['remote', '; '.join(group), coordinates[0], coordinates[1], 'ADD FUNCTIONALITY LATER'])
        
    
    