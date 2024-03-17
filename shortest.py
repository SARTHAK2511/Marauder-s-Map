import requests
import random
from haversine import haversine
import folium
import math
from geopy.geocoders import Nominatim

def reverse_geocode(lat, lon):
    geolocator = Nominatim(user_agent="reverse_geocode_app")
    location = geolocator.reverse((lat, lon), language='en')
    return location.address

def get_overpass_data(start_coord, end_coord):
    north = max(start_coord[0], end_coord[0])
    south = min(start_coord[0], end_coord[0])
    east = max(start_coord[1], end_coord[1])
    west = min(start_coord[1], end_coord[1])

    overpass_url = 'https://overpass-api.de/api/interpreter'
    overpass_query = f'''
    [out:json];
    (
      way({south},{west},{north},{east})[highway];
      >;
    );
    out body;
    '''
    print(overpass_query)
    response = requests.get(overpass_url, params={'data': overpass_query})
    return response.json()

def find_closest_node(target_coords, nodes):
    min_distance = float('inf')
    closest_node_id = None
    for node in nodes:
        if 'lat' in node and 'lon' in node:
            node_coords = (node['lat'], node['lon'])
            distance = haversine(target_coords, node_coords)
            if distance < min_distance:
                min_distance = distance
                closest_node_id = node['id']
    return closest_node_id

def heuristic(node1, node2, nodes_info):
    coord1 = (nodes_info[node1]['lat'], nodes_info[node1]['lon'])
    coord2 = (nodes_info[node2]['lat'], nodes_info[node2]['lon'])
    return haversine(coord1, coord2)

def a_star(graph, start, goal, heuristic, nodes_info):
    open_set = {start}
    came_from = {}
    g_score = {node: float('inf') for node in graph}
    g_score[start] = 0
    f_score = {node: float('inf') for node in graph}
    f_score[start] = heuristic(start, goal, nodes_info)

    while open_set:
        current = min(open_set, key=lambda node: f_score[node])
        if current == goal:
            return reconstruct_path(came_from, current)

        open_set.remove(current)
        for neighbor in graph[current]:
            tentative_g_score = g_score[current] + graph[current][neighbor]
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal, nodes_info)
                if neighbor not in open_set:
                    open_set.add(neighbor)
    return []

def reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.insert(0, current)
    return total_path

def create_route_map(start_coords, end_coords, nodes):
    nodes_info = {node['id']: node for node in nodes['elements']}
    graph = {}
    for node in nodes['elements']:
        if 'lat' in node and 'lon' in node:
            graph[node['id']] = {}
    for element in nodes['elements']:
        if element['type'] == 'way':
            for i in range(len(element['nodes']) - 1):
                distance = heuristic(element['nodes'][i], element['nodes'][i + 1], nodes_info)
                graph[element['nodes'][i]][element['nodes'][i + 1]] = distance
                graph[element['nodes'][i + 1]][element['nodes'][i]] = distance

    start_node_id = find_closest_node(start_coords, nodes['elements'])
    end_node_id = find_closest_node(end_coords, nodes['elements'])

    path = a_star(graph, start_node_id, end_node_id, heuristic, nodes_info)
    return path, nodes_info

def plot_path_on_map(start_coords, end_coords, path, nodes_info):
    map_center = [(start_coords[0] + end_coords[0]) / 2, (start_coords[1] + end_coords[1]) / 2]
    map = folium.Map(location=map_center, zoom_start=15)
    folium.Marker(start_coords, popup='Start', icon=folium.Icon(color='green')).add_to(map)
    # folium.Marker(end_coords, popup='End', icon=folium.Icon(color='red')).add_to(map)
    path_coords = [(nodes_info[node_id]['lat'], nodes_info[node_id]['lon']) for node_id in path]
    folium.PolyLine(path_coords, color="blue", weight=2.5, opacity=1).add_to(map)

        # Calculate total distance of the path
    total_distance = 0
    for i in range(len(path) - 1):
        node1_coords = (nodes_info[path[i]]['lat'], nodes_info[path[i]]['lon'])
        node2_coords = (nodes_info[path[i+1]]['lat'], nodes_info[path[i+1]]['lon'])
        total_distance += haversine(node1_coords, node2_coords)
            
    preference = ['auto', 'cab']
    fare_estimate = get_manual_taxi_fare_estimate(total_distance, preference[1])
    ola_link = "https://www.olacabs.com/"
    uber_link = "https://www.uber.com/in/en/"
    distance_popup = f'Total Distance: {total_distance:.2f} km \n\n Fare Estimate: {fare_estimate}\n\n'

      
    print(distance_popup)
    folium.Marker(path_coords[-1], popup=distance_popup, icon=folium.Icon(color='purple')).add_to(map)
    
    return map, total_distance

def get_manual_taxi_fare_estimate(distance_km, type):
    # Define fare estimates for different distance ranges
    if type == 'auto':
        if distance_km <= 2:
            return "Rs 14 - Rs 26"
        elif 2 < distance_km <= 4:
            return "Rs 27 - Rs 36"
        elif 4 < distance_km <= 6:
            return "Rs 56 - Rs 77"
        elif 6 < distance_km <= 8:
            return "Rs 76 - Rs 93"
        elif 8 < distance_km <= 10:
            return "Rs 93 - Rs 116"
        elif 10 < distance_km <= 12:
            return "Rs 112 - Rs 134"
        elif 12 < distance_km <= 14:
            return "Rs 133 - Rs 156"
        elif 14 < distance_km <= 16:
            return "Rs 154 - Rs 166"
        elif 16 < distance_km <= 18:
            return "Rs 164 - Rs 182"
        elif 18 < distance_km <= 20:
            return "Rs 181 - Rs 195"
        else:
            return "Distance exceeds 20km. Please consult local taxi service for fare."
    else:
        if distance_km <= 2:
            return "Rs 21 - Rs 34"
        elif 2 < distance_km <= 4:
            return "Rs 36 - Rs 54"
        elif 4 < distance_km <= 6:
            return "Rs 64 - Rs 87"
        elif 6 < distance_km <= 8:
            return "Rs 72 - Rs 119"
        elif 8 < distance_km <= 10:
            return "Rs 93 - Rs 128"
        elif 10 < distance_km <= 12:
            return "Rs 121 - Rs 146"
        elif 12 < distance_km <= 14:
            return "Rs 134 - Rs 153"
        elif 14 < distance_km <= 16:
            return "Rs 134 - Rs 166"
        elif 16 < distance_km <= 18:
            return "Rs 165 - Rs 182"
        elif 18 < distance_km <= 20:
            return "Rs 182 - Rs 213"
        else:
            return "Distance exceeds 20km. Please consult local taxi service for fare."




def calculate_shortest(start_coords, end_coords):
# Get the addresses of start and end coordinates

    # source_address = reverse_geocode(start_coords['lat'], start_coords['lng'])
    # destination_address = reverse_geocode(end_coords['lat'], end_coords['lng'])

    # print("Source:", source_address)
    # print("Destination:", destination_address)
    start_coords=tuple(start_coords.values())
    end_coords=tuple(end_coords.values())
    print(start_coords,end_coords)
    # Get data from Overpass API
    nodes = get_overpass_data(start_coords, end_coords)

    # Create route map
    path, nodes_info = create_route_map(start_coords, end_coords, nodes)

    # Plot the path on the map and get total distance
    path_map, total_distance = plot_path_on_map(start_coords, end_coords, path, nodes_info)

    # Save the map
    path_map.save(r'D:\Application\Marauder-s-Map\templates\shortest.html')

    # # Print total distance
    # print(f"Total Distance: {total_distance:.2f} km")

    # # Calculate taxi fare estimate
    # preference = ['auto', 'cab']
    # fare_estimate = get_manual_taxi_fare_estimate(total_distance, preference[1])
    # print("Taxi Fare Estimate:", fare_estimate)



    # You can return any additional data if needed
    return  1

