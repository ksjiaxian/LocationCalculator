#import requests
import formulas
import csv
import requests

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
            if dist <= float(r1):
                local_set.add(other_location)
        local_set_list.append((location, local_set))
    
    #local set around focal point of locations in (address, lat, long)
    local_set = set()
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
    remote_set = set()

    lat1 = focal_point[0]
    lon1 = focal_point[1]
    for loc in location_list:
        lat2 = loc[0]
        lon2 = loc[1]
        dist = formulas.haversine(lat1, lon1, lat2, lon2)
        if dist > float(r2):
            remote_set.add(loc)
    return remote_set

def generate_geo_relationship(country1, other_center):
    #this is for using the bing reverse geocode api
    coord2 = other_center[0] +","+ other_center[1]
    response2 = requests.get("http://dev.virtualearth.net/REST/v1/Locations/" + coord2,
                params={"key":"AjhzSUKjNFFV0ckKVCV64tSLhw_EWSlN6LP9UPiWdEJDRMZn3Vm17HtoSclZZfO_ ",
                        })
    data2 = response2.json()
    #get the country data
        
    try:
        country2 = str(data2['resourceSets'][0]['resources'][0]['address']['countryRegion'])
    except:
        country2 = "N/A"
      
    if country1 == country2:
        if country1 == "N/A":
            return (country1, country2, "N/A")
        else: 
            return (country1, country2, "domestic")
    else:
        return (country1, country2, "cross border")

if __name__ == '__main__':
    ungrouped = []
    r1 = 0
    r2 = 0
    with open('inputs/input.tsv', encoding='latin-1') as tsvfile:
        reader = csv.DictReader(tsvfile, dialect='excel-tab')
        
        #create the set of ungrouped addresses
        for row in reader:
            lat = row['lat']
            lng = row['lng']
            
            ungrouped.append((lat, lng))
            
    with open('inputs/arguments.csv', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        
        #create the list of ungrouped addresses
        for row in reader:
            r1 = row['r1']
            r2 = row['r2']
    
    #get the local locations
    (local_center, local_set) = get_focal_point(ungrouped, r1)
    #get the remote locations
    remote_set = create_remote_set(local_center, ungrouped, r2)
    #find the locations that are not local and not remote
    inbetween = set(ungrouped) - remote_set - local_set
    # get local country
    coord1 = local_center[0] +","+ local_center[1]
    response1 = requests.get("http://dev.virtualearth.net/REST/v1/Locations/" + coord1,
                params={"key":"AjhzSUKjNFFV0ckKVCV64tSLhw_EWSlN6LP9UPiWdEJDRMZn3Vm17HtoSclZZfO_ ",
                        })
    data1 = response1.json()
    #get the country data
    try:
        country1 = str(data1['resourceSets'][0]['resources'][0]['address']['countryRegion'])
    except:
        country1 = "N/A"
        
    
    #list of sets of remote groups
    remote_groups = []
    
    while len(remote_set) > 0:
        #get largest remote group, add to remote groups and remove from set of ungrouped remotes
        remote_group = get_focal_point(remote_set, r1)
        remote_groups.append(remote_group)
        remote_set -= remote_group[1]
       
    with open('outputs/new_output8.csv', 'w', newline="\n", encoding='latin-1') as out_file: 
        csv_writer = csv.writer(out_file, delimiter=',')
        header = ["group_classification", "locations", "point_lat", "point_lng", "country", "geographical_relationship", 
                  "haversine_distance_to_local"]
        csv_writer.writerow(header)
    
        # convert local_set from a set of tuples to a list of strings
        local_set_string = []
        for (lat, lon) in local_set:
            coord = '(' + str(lat) + ',' + str(lon) +')'
            local_set_string.append(coord)
            
        csv_writer.writerow(['local', '; '.join(local_set_string), local_center[0], local_center[1], country1, 'domestic', 'N/A', 'N/A'])
        
        # convert local_set from a set of tuples to a list of strings
        inbetween_set_string = []
        for (lat, lon) in inbetween:
            coord = '(' + str(lat) + ',' + str(lon) +')'
            inbetween_set_string.append(coord)
        csv_writer.writerow(['non-local', '; '.join(inbetween_set_string), 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'])
        
        # sort remote groups by distance away from local focal point
        remote_group_list = []
        for remote_group in remote_groups:
            (coordinates, group) = remote_group
            dist = formulas.haversine(local_center[0], local_center[1], coordinates[0], coordinates[1])
            remote_group_list.append((coordinates, group, dist))
            remote_group_list.sort(key=lambda tup: tup[2])  # sorts in place
        
        for remote_group in remote_group_list:
            (coordinates, group, dist) = remote_group
            # convert remote_group from a set of tuples to a list of strings
            remote_group_string = []
            for (lat, lon) in group:
                coord = '(' + str(lat) + ',' + str(lon) +')'
                remote_group_string.append(coord)
            (c1, c2, rel) = generate_geo_relationship(country1, coordinates)
            csv_writer.writerow(['remote', '; '.join(remote_group_string), coordinates[0], coordinates[1], c2, rel, 
                                 formulas.haversine(local_center[0], local_center[1], coordinates[0], coordinates[1])])
            
        
    