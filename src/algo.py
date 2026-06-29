from collections import deque
import heapq
from model import Node

TERRAIN_COSTS = {
    '0': 1,   # Đất bằng
    'K': 1,   # Hiệp sĩ
    'P': 1,   # Công chúa
    '2': 5,   # Đầm lầy
    'M': 50   # Vùng quái
}

def get_cost(matrix, r, c):
    terrain_type = matrix[r][c]
    return TERRAIN_COSTS.get(terrain_type, float('inf'))

def get_neighbors(node, matrix):
    neighbors = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    rows, cols = len(matrix), len(matrix[0])
    for dr, dc in directions:
        nr, nc = node.x + dr, node.y + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            if matrix[nr][nc] != '1': 
                neighbors.append(Node(nr, nc, node))
    return neighbors

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def reconstruct_path(end_node):
    path = []
    curr = end_node
    while curr:
        path.append((curr.x, curr.y))
        curr = curr.parent
    return path[::-1]

def BFS(matrix, start, end):
    start_node = Node(start[0], start[1])
    queue = deque([start_node])
    visited = {start}
    
    visited_nodes = 0
    max_queue_size = 1

    while queue:
        max_queue_size = max(max_queue_size, len(queue))
        curr_node = queue.popleft()
        visited_nodes += 1

        if (curr_node.x, curr_node.y) == end:
            return reconstruct_path(curr_node), visited_nodes, max_queue_size

        for neighbor in get_neighbors(curr_node, matrix):
            pos = (neighbor.x, neighbor.y)
            if pos not in visited:
                visited.add(pos)
                queue.append(neighbor)
    return [], visited_nodes, max_queue_size

def DFS(matrix, start, end):
    start_node = Node(start[0], start[1])
    stack = [start_node]
    visited = {start}
    
    visited_nodes = 0
    max_queue_size = 1

    while stack:
        max_queue_size = max(max_queue_size, len(stack))
        curr_node = stack.pop()
        visited_nodes += 1

        if (curr_node.x, curr_node.y) == end:
            return reconstruct_path(curr_node), visited_nodes, max_queue_size

        for neighbor in get_neighbors(curr_node, matrix):
            pos = (neighbor.x, neighbor.y)
            if pos not in visited:
                visited.add(pos)
                stack.append(neighbor)
    return [], visited_nodes, max_queue_size

def UCS(matrix, start, end):
    start_node = Node(start[0], start[1])
    start_node.g = 0
    counter = 0
    heap = [(0, counter, start_node)]
    best_g = {start: 0}
    
    visited_nodes = 0
    max_queue_size = 1

    while heap:
        max_queue_size = max(max_queue_size, len(heap))
        g, _, curr_node = heapq.heappop(heap)
        visited_nodes += 1

        if (curr_node.x, curr_node.y) == end:
            return reconstruct_path(curr_node), visited_nodes, max_queue_size

        if curr_node.g > best_g.get((curr_node.x, curr_node.y), float('inf')):
            continue

        for neighbor in get_neighbors(curr_node, matrix):
            step_cost = get_cost(matrix, neighbor.x, neighbor.y)
            new_g = curr_node.g + step_cost
            pos = (neighbor.x, neighbor.y)

            if new_g < best_g.get(pos, float('inf')):
                best_g[pos] = new_g
                neighbor.g = new_g
                counter += 1
                heapq.heappush(heap, (new_g, counter, neighbor))
    return [], visited_nodes, max_queue_size

def Greedy(matrix, start, end):
    start_node = Node(start[0], start[1])
    start_node.h = heuristic(start, end)
    counter = 0
    heap = [(start_node.h, counter, start_node)]
    visited = {start}
    
    visited_nodes = 0
    max_queue_size = 1

    while heap:
        max_queue_size = max(max_queue_size, len(heap))
        h, _, curr_node = heapq.heappop(heap)
        visited_nodes += 1

        if (curr_node.x, curr_node.y) == end:
            return reconstruct_path(curr_node), visited_nodes, max_queue_size

        for neighbor in get_neighbors(curr_node, matrix):
            pos = (neighbor.x, neighbor.y)
            if pos not in visited:
                visited.add(pos)
                neighbor.h = heuristic(pos, end)
                counter += 1
                heapq.heappush(heap, (neighbor.h, counter, neighbor))
    return [], visited_nodes, max_queue_size

def Astar(matrix, start, end):
    start_node = Node(start[0], start[1])
    start_node.g = 0
    start_node.h = heuristic(start, end)
    start_node.f = start_node.g + start_node.h
    counter = 0
    heap = [(start_node.f, counter, start_node)]
    best_g = {start: 0}
    
    visited_nodes = 0
    max_queue_size = 1

    while heap:
        max_queue_size = max(max_queue_size, len(heap))
        f, _, curr_node = heapq.heappop(heap)
        visited_nodes += 1

        if (curr_node.x, curr_node.y) == end:
            return reconstruct_path(curr_node), visited_nodes, max_queue_size

        if curr_node.g > best_g.get((curr_node.x, curr_node.y), float('inf')):
            continue

        for neighbor in get_neighbors(curr_node, matrix):
            step_cost = get_cost(matrix, neighbor.x, neighbor.y)
            new_g = curr_node.g + step_cost
            pos = (neighbor.x, neighbor.y)

            if new_g < best_g.get(pos, float('inf')):
                best_g[pos] = new_g
                neighbor.g = new_g
                neighbor.h = heuristic(pos, end)
                neighbor.f = new_g + neighbor.h
                counter += 1
                heapq.heappush(heap, (neighbor.f, counter, neighbor))
    return [], visited_nodes, max_queue_size