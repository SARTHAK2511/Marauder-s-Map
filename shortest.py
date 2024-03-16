import requests
from haversine import haversine
import folium
import math

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

def heuristic_with_noise(node1, node2, nodes_info):
    # Calculate distance heuristic (e.g., Euclidean distance)
    coord1 = (nodes_info[node1]['lat'], nodes_info[node1]['lon'])
    coord2 = (nodes_info[node2]['lat'], nodes_info[node2]['lon'])
    distance_heuristic = haversine(coord1, coord2)
    
    # Incorporate noise levels into the heuristic calculation
    # noise_level = get_avg_noise_level_along_path(coord1, coord2, noise_data)
    noise_level = 0.1
    weight_factor = 0.9
    
    # Combine distance and noise heuristics (adjust weights as needed)
    combined_heuristic = distance_heuristic + noise_level * weight_factor
    
    return combined_heuristic

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
                distance = heuristic_with_noise(element['nodes'][i], element['nodes'][i + 1], nodes_info)
                graph[element['nodes'][i]][element['nodes'][i + 1]] = distance
                graph[element['nodes'][i + 1]][element['nodes'][i]] = distance

    start_node_id = find_closest_node(start_coords, nodes['elements'])
    end_node_id = find_closest_node(end_coords, nodes['elements'])

    path = a_star(graph, start_node_id, end_node_id, heuristic_with_noise, nodes_info)
    return path, nodes_info


# def plot_path_on_map(start_coords, end_coords, path, nodes_info):
#     map_center = [(start_coords[0] + end_coords[0]) / 2, (start_coords[1] + end_coords[1]) / 2]
#     map = folium.Map(location=map_center, zoom_start=15)
#     folium.Marker(start_coords, popup='Start', icon=folium.Icon(color='green')).add_to(map)
#     folium.Marker(end_coords, popup='End', icon=folium.Icon(color='red')).add_to(map)
#     path_coords = [(nodes_info[node_id]['lat'], nodes_info[node_id]['lon']) for node_id in path]
#     folium.PolyLine(path_coords, color="blue", weight=2.5, opacity=1).add_to(map)
    # return map

def plot_path_on_map(start_coords, end_coords, path, nodes_info):
    map_center = [(start_coords[0] + end_coords[0]) / 2, (start_coords[1] + end_coords[1]) / 2]
    map = folium.Map(location=map_center, zoom_start=15)
    folium.Marker(start_coords, popup='Start', icon=folium.Icon(color='green')).add_to(map)
    folium.Marker(end_coords, popup='End', icon=folium.Icon(color='red')).add_to(map)
    path_coords = [(nodes_info[node_id]['lat'], nodes_info[node_id]['lon']) for node_id in path]
    folium.PolyLine(path_coords, color="blue", weight=2.5, opacity=1).add_to(map)
    
    # Calculate total distance of the path
    total_distance = 0
    for i in range(len(path) - 1):
        node1_coords = (nodes_info[path[i]]['lat'], nodes_info[path[i]]['lon'])
        node2_coords = (nodes_info[path[i+1]]['lat'], nodes_info[path[i+1]]['lon'])
        total_distance += haversine(node1_coords, node2_coords)
    
    # Add distance information to map
    distance_popup = f'Total Distance(Quiteness): {total_distance:.2f} km'
    print(distance_popup)
    folium.Marker(path_coords[-1], popup=distance_popup, icon=folium.Icon(color='purple')).add_to(map)
    
    return map



# Example usage
start_coords = (22.689221, 75.874243)  # hackhive
end_coords = (22.729245, 75.813475)    # airport
nodes = get_overpass_data(start_coords, end_coords)

path, nodes_info = create_route_map(start_coords, end_coords, nodes)
path_map = plot_path_on_map(start_coords, end_coords, path, nodes_info)
path_map.save('path_map_withNoise.html')