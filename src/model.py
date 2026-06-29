import os

TILE_SIZE = 48
BANNER_WIDTH = 230
MAP_OFFSET_X = BANNER_WIDTH

class Node:
    def __init__(self, x, y, parent=None):
        self.x = x
        self.y = y
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        if other is None: 
            return False
        return self.x == other.x and self.y == other.y

class MazeModel:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.map_folder_path = os.path.join(base_dir, 'map')

        all_files = os.listdir(self.map_folder_path)
        self.map_files = sorted([f for f in all_files if f.startswith('map') and f.endswith('.txt')])

        if not self.map_files:
            raise FileNotFoundError(
                f"\n[LỖI] Không tìm thấy file map*.txt nào bên trong thư mục 'map'!\n"
                f"Đường dẫn hiện tại hệ thống đang quét: {self.map_folder_path}\n"
                f"Hãy chắc chắn các file có tên chính xác dạng: map1.txt, map2.txt (viết thường)\n"
            )
            
        self.current_map_idx = 0
        
        first_map_path = os.path.join(self.map_folder_path, self.map_files[self.current_map_idx])
        self.matrix, self.start_pos, self.end_pos = self._load_map(first_map_path)

        self.knight_pos = self.start_pos
        self.path = []
        self.path_index = 0
        self.moving = False
        self.game_won = False  
        self.path_cost = 0  
        self.active_algo = "None"

        # --- PHẦN THÊM MỚI CHO LỊCH SỬ ---
        self.history_log = [] 
        self.show_history = False 

    def _load_map(self, filename):
        matrix = []
        start_pos, end_pos = None, None
        with open(filename, 'r') as f:
            for r, line in enumerate(f):
                row = line.strip().split()
                if not row: continue
                for c, val in enumerate(row):
                    if val == 'K': start_pos = (r, c)
                    elif val == 'P': end_pos = (r, c)
                matrix.append(row)
        return matrix, start_pos, end_pos
    
    def reset(self):
        current_map_path = os.path.join(self.map_folder_path, self.map_files[self.current_map_idx])
        self.matrix, self.start_pos, self.end_pos = self._load_map(current_map_path)
        self.knight_pos = self.start_pos
        self.path = []
        self.path_index = 0
        self.moving = False
        self.game_won = False
        self.path_cost = 0
        self.active_algo = "None"
        self.show_history = False

    def load_next_map(self):
        if self.current_map_idx + 1 < len(self.map_files):
            self.current_map_idx += 1
            next_map_path = os.path.join(self.map_folder_path, self.map_files[self.current_map_idx])
            self.matrix, self.start_pos, self.end_pos = self._load_map(next_map_path)
            self.reset()
            return True 
        return False  

    def update_physics(self):
        if self.moving and self.path:
            if self.path_index < len(self.path):
                self.knight_pos = self.path[self.path_index]
                self.path_index += 1

                r, c = self.knight_pos
                if self.matrix[r][c] == 'M':
                    self.matrix[r][c] = '0'

                if self.knight_pos == self.end_pos:
                    self.moving = False
                    self.game_won = True
            else:
                self.moving = False # <--- THÊM/ĐẢM BẢO CÓ DÒNG NÀY
                if self.knight_pos == self.end_pos:
                    self.game_won = True
                
    def set_path(self, new_path):
        if new_path:
            self.path = new_path
            self.path_index = 0
            self.moving = True
            self.game_won = False
            
            costs = {'0': 1, 'K': 1, 'P': 1, '2': 5, 'M': 50}
            self.path_cost = sum(costs.get(self.matrix[r][c], 1) for r, c in new_path[1:])

    def move_manual(self, dr, dc):
        if self.game_won or self.moving or self.show_history:
            return 
            
        r, c = self.knight_pos
        nr, nc = r + dr, c + dc
        
        if 0 <= nr < len(self.matrix) and 0 <= nc < len(self.matrix[0]):
            if self.matrix[nr][nc] != '1':
                if not self.path:
                    self.path = [self.knight_pos]
                    self.path_index = 1
                    
                self.knight_pos = (nr, nc)
                self.path.append(self.knight_pos)
                self.path_index += 1

                costs = {'0': 1, 'K': 1, 'P': 1, '2': 5, 'M': 50}
                self.path_cost += costs.get(self.matrix[nr][nc], 1)

                if self.matrix[nr][nc] == 'M':
                    self.matrix[nr][nc] = '0'
                
                if self.knight_pos == self.end_pos:
                    self.game_won = True
                    
    # --- PHẦN THÊM MỚI: HÀM LƯU LỊCH SỬ ---
    def add_history_record(self, algo_name, search_time_ms, cost, steps, visited_nodes, max_queue):
        """Thêm bản ghi lịch sử ban đầu kèm các thông số AI chuyên sâu"""
        efficiency = (steps / visited_nodes * 100) if visited_nodes > 0 else 0.0
        self.history_log.append({
            'name': algo_name,
            'search_time': search_time_ms,
            'run_time': 0.0,
            'cost': cost,
            'steps': steps,
            'visited': visited_nodes,
            'max_queue': max_queue,
            'efficiency': efficiency,
            'status': 'Đang đi...'
        })

    def update_last_record_run_time(self, run_time_sec, is_cancelled=False):
        """Cập nhật thời gian chạy thực tế và trạng thái cuối cùng"""
        if self.history_log:
            self.history_log[-1]['run_time'] = run_time_sec
            if is_cancelled:
                self.history_log[-1]['status'] = 'Bị hủy'
            else:
                self.history_log[-1]['status'] = 'Thành công' if self.game_won else 'Thất bại'

                # --- PHẦN THÊM MỚI: HÀM LƯU BẢN ĐỒ CHO EDITMAP ---
    def save_map(self):
        """Lưu trạng thái ma trận hiện tại ghi đè vào file map đang chơi"""
        current_map_path = os.path.join(self.map_folder_path, self.map_files[self.current_map_idx])
        with open(current_map_path, 'w') as f:
            for row in self.matrix:
                f.write(" ".join(row) + "\n")
        return current_map_path