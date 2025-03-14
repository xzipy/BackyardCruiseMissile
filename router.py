import heapq
import random
from shapely.geometry import Point, Polygon
from geopy.distance import geodesic

# Function to check if the coordinate is within any no-zone polygon
def is_in_no_zone(coord, no_zones):
    point = Point(coord)
    for zone in no_zones:
        polygon = Polygon(zone)
        if polygon.contains(point):
            return True
    return False

# Function to generate a random endpoint that is not inside a no-zone
def generate_random_endpoint(start_point, no_zones, max_attempts=100):
    attempts = 0
    while attempts < max_attempts:
        random_endpoint = (start_point[0] + random.uniform(-0.05, 0.05), start_point[1] + random.uniform(-0.05, 0.05))
        if not is_in_no_zone(random_endpoint, no_zones):
            return random_endpoint
        attempts += 1
    return None  # No valid random endpoint found within attempts

# Function to calculate the geodesic distance between two points
def calculate_distance(point1, point2):
    return geodesic(point1, point2).meters

# Dijkstra's Algorithm to find the shortest path
def dijkstra(start, end, graph, no_zones):
    # Priority queue to store (distance, node)
    queue = [(0, start)]
    # Dictionary to store shortest distances
    distances = {start: 0}
    # Dictionary to store the previous node for path reconstruction
    previous_nodes = {start: None}
    
    while queue:
        # Get the node with the smallest distance
        current_distance, current_node = heapq.heappop(queue)

        # If we reached the end node, reconstruct the path
        if current_node == end:
            path = []
            while current_node is not None:
                path.append(current_node)
                current_node = previous_nodes[current_node]
            return path[::-1]  # Return reversed path
        
        # Process all neighbors (adjacent nodes)
        for neighbor, distance in graph.get(current_node, []):
            # Skip if the neighbor is inside a no-zone
            if is_in_no_zone(neighbor, no_zones):
                continue

            new_distance = current_distance + distance
            if neighbor not in distances or new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(queue, (new_distance, neighbor))
    
    return None  # No path found

# Function to create a graph from nearby coordinates
def create_graph(start_point, no_zones, grid_size=0.001, max_distance=1000):
    # Create a grid of points around the start_point
    nodes = []
    for lat_offset in [-grid_size, 0, grid_size]:
        for lon_offset in [-grid_size, 0, grid_size]:
            new_point = (start_point[0] + lat_offset, start_point[1] + lon_offset)
            if not is_in_no_zone(new_point, no_zones):
                nodes.append(new_point)
    
    # Create edges between nodes that are within max_distance
    graph = {}
    for node in nodes:
        graph[node] = []
        for neighbor in nodes:
            if node != neighbor:
                dist = calculate_distance(node, neighbor)
                if dist <= max_distance:
                    graph[node].append((neighbor, dist))
    
    return graph

def create_optimal_route(start_point, no_zone_json):
    no_zones = [zone['coordinates'] for zone in no_zone_json]
    
    random_end = generate_random_endpoint(start_point, no_zones)
    if not random_end:
        return None  # No valid endpoint found
    
    graph = create_graph(start_point, no_zones)
    
    optimal_route = dijkstra(start_point, random_end, graph, no_zones)
    
    return optimal_route
