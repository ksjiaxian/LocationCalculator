import requests
import formulas

# list of locations in (address, lat, long)
location_list = None

# local radius
r1 = 0
# remote radius
r2 = 0
# focal point
focal_point = None
#local set around focal point of locations in (address, lat, long)
local_set = None
#list of location set around every point in tuple form (location, set)
local_set_list = []
#remote set around focal point of locations in (address, lat, long)
remote_set = None

def get_focal_point(address_list, local_radius, remote_radius):
    global r1
    global r2
    r1 = local_radius
    r2 = remote_radius
    
    # get lat and long for each address
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
    
    global local_set_list
    # iterate through location_list to create sets for each location
    for location in location_list:
        lat1 = location[1]
        lon1 = location[2]
        local_set = set()
        for other_location in location_list:
            lat2 = other_location[1]
            lon2 = other_location[2]
            dist = formulas.haversine(lat1, lon1, lat2, lon2)
            if dist <= r1:
                local_set.add(other_location)
        local_set_list.append((location, local_set))
    
    global local_set
    global focal_point
    #iterate through dictionary to get largest set and focal point
    for loc, self_set in local_set_list:
        if (len(self_set) > len(local_set)):
            local_set = self_set
            focal_point = loc
    
    return (focal_point, local_set)

def create_remote_set():
    if focal_point == None:
        print("Call get_focal_point first")
    else:  
        lat1 = focal_point[1]
        lon1 = focal_point[2]
        for loc in location_list:
            lat2 = loc[1]
            lon2 = loc[2]
            dist = formulas.haversine(lat1, lon1, lat2, lon2)
            if dist > r2:
                remote_set 


if __name__ == '__main__':