import heapq, random, json
from shapely.geometry import Point, Polygon, LineString
from geopy.distance import geodesic

def is_in_no_zone(coord, no_zones):
    point = Point(coord)
    for zone in no_zones:
        polygon = Polygon(zone)
        if polygon.contains(point):
            return True
    return False

def edge_intersects_no_zone(point1, point2, no_zones):
    line = LineString([point1, point2])
    for zone in no_zones:
        polygon = Polygon(zone)
        if line.intersects(polygon):
            return True
    return False

# Function to generate a random endpoint that is not inside a no-zone
def generate_random_endpoint(start_point, no_zones, max_attempts=100):
    attempts = 0
    while attempts < max_attempts:
        random_endpoint = (start_point[0] + random.uniform(-0.05, 0.05), start_point[1] + random.uniform(-0.05, 0.05))
        if not is_in_no_zone(random_endpoint, no_zones):
            print(f'Generated random endpoint: {random_endpoint} after {attempts + 1} attempts')
            return random_endpoint
        attempts += 1
    print("No valid random endpoint found within attempts")
    return None  # No valid random endpoint found within attempts

# Function to calculate the geodesic distance between two points
def calculate_distance(point1, point2):
    return geodesic(point1, point2).meters

# Dijkstra's Algorithm to find the shortest path
def dijkstra(start, end, graph, no_zones):
    print(f'Starting Dijkstra from {start} to {end}')
    # Priority queue to store (distance, node)
    queue = [(0, start)]
    # Dictionary to store shortest distances
    distances = {start: 0}
    # Dictionary to store the previous node for path reconstruction
    previous_nodes = {start: None}
    
    while queue:
        # Get the node with the smallest distance
        current_distance, current_node = heapq.heappop(queue)
        print(f'Visiting node {current_node} with current distance {current_distance}')

        # If we reached the end node, reconstruct the path
        if current_node == end:
            path = []
            while current_node is not None:
                path.append(current_node)
                current_node = previous_nodes[current_node]
            print(f'Path found: {path[::-1]}')
            return path[::-1]  # Return reversed path
        
        # Process all neighbors (adjacent nodes)
        for neighbor, distance in graph.get(current_node, []):
            # Skip if the neighbor is inside a no-zone
            if is_in_no_zone(neighbor, no_zones):
                print(f'Skipping neighbor {neighbor} as it is in a no-zone')
                continue

            new_distance = current_distance + distance
            if neighbor not in distances or new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(queue, (new_distance, neighbor))
                print(f'Updating distance for neighbor {neighbor} to {new_distance}')
    
    print('No path found')
    return None  # No path found

# Function to create a graph from nearby coordinates
def create_graph(start_point, end_point, no_zones, grid_size=0.001, max_distance=1000):
    print(f'Creating graph around start point {start_point} and end point {end_point}')
    # Create a grid of points around the start_point
    nodes = []
    for lat_offset in [-grid_size, 0, grid_size]:
        for lon_offset in [-grid_size, 0, grid_size]:
            new_point = (start_point[0] + lat_offset, start_point[1] + lon_offset)
            if not is_in_no_zone(new_point, no_zones):
                nodes.append(new_point)
    
    # Add extra waypoints around no-zones
    for zone in no_zones:
        for point in zone:
            for lat_offset in [-grid_size, 0, grid_size]:
                for lon_offset in [-grid_size, 0, grid_size]:
                    new_point = (point[0] + lat_offset, point[1] + lon_offset)
                    if not is_in_no_zone(new_point, no_zones):
                        nodes.append(new_point)
    
    # Ensure the end point is included in the nodes
    if not is_in_no_zone(end_point, no_zones):
        nodes.append(end_point)
    print(f'Generated nodes: {nodes}')
    
    # Create edges between nodes that are within max_distance
    graph = {}
    for node in nodes:
        graph[node] = []
        for neighbor in nodes:
            if node != neighbor:
                dist = calculate_distance(node, neighbor)
                if dist <= max_distance and not is_in_no_zone(neighbor, no_zones):
                    # Ensure the edge does not intersect any no-zone
                    if not edge_intersects_no_zone(node, neighbor, no_zones):
                        graph[node].append((neighbor, dist))
    print(f'Generated graph: {graph}')
    
    return graph

def create_route(end_point):
    start_point = (35.873436430190836, -78.60693661720285)
    print(f'Starting point: {start_point}')
    print(f'End point: {end_point}')
    
    with open("mapMarkers.json", "r") as file:
        jsonData = json.load(file)

    no_zones = []
    for i in jsonData["noZones"]:
        no_zones.append(jsonData["noZones"][i])
    print(f'No zones: {no_zones}')

    start_point = (float(start_point[0]), float(start_point[1]))
    end_point = (float(end_point[0]), float(end_point[1]))
    print(f'Converted starting point: {start_point}')
    print(f'Converted end point: {end_point}')
    
    graph = create_graph(start_point, end_point, no_zones)
    print(f'Generated graph: {graph}')
    
    optimal_route = dijkstra(start_point, end_point, graph, no_zones)
    print(f'Optimal route: {optimal_route}')
    
    return optimal_route