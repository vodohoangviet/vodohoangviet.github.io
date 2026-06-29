import pygame
import sys
import time
from algo import BFS, DFS, UCS, Greedy, Astar
from editmap import MapEditor

class GameController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.clock = pygame.time.Clock()
        self.running = True

        self.knight_move_delay = 200  
        self.last_knight_move_time = pygame.time.get_ticks()
        
        self.start_move_time = None
        self.is_tracking_move = False

        #Khởi tạo bộ chỉnh sửa bản đồ
        self.editor = MapEditor(self.model, self.view)

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.handle_events()

            # Không cập nhật vật lý di chuyển nếu đang mở lịch sử HOẶC đang bật Edit bản đồ
            if not self.model.show_history and not self.editor.active:
                now = pygame.time.get_ticks()
                if now - self.last_knight_move_time >= self.knight_move_delay:
                    self.model.update_physics()
                    self.last_knight_move_time = now
            
            if self.model.moving and not self.is_tracking_move:
                self.start_move_time = time.perf_counter()
                self.is_tracking_move = True
            
            if self.model.game_won and self.is_tracking_move:
                end_move_time = time.perf_counter()
                total_run_time = end_move_time - self.start_move_time
                self.model.update_last_record_run_time(total_run_time)
                self.is_tracking_move = False

            # Truyền thêm đối tượng editor vào render để View có thể vẽ vùng highlight và thông báo
            self.view.render(self.model, self.editor)
        
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            if self.model.show_history:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    if self.view.close_history_btn and self.view.close_history_btn.collidepoint(mouse_pos):
                        self.model.show_history = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_x]:
                        self.model.show_history = False
                continue

            # --- XỬ LÝ SỰ KIỆN EDIT MAP BẰNG NÚT CÔNG TẮC ---
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.view.edit_switch_rect and self.view.edit_switch_rect.collidepoint(event.pos):
                    # không cho phép sửa khi nhân vật di chuyển hoặc đã chiến thắng
                    if not self.model.moving and not self.model.game_won:
                        self.editor.toggle()
                        if self.editor.active and self.model.path:
                            self.model.reset() # Xóa đường đi cũ nếu bật chế độ chỉnh sửa
                        continue
            
            # --- XỬ LÝ SỰ KIỆN EDIT MAP BẰNG PHÍM [E] ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.editor.toggle()
                    if self.editor.active and self.model.path:
                        self.model.reset() # Reset đường đi cũ nếu vào chế độ chỉnh sửa tránh lỗi hiển thị
                    continue
                
                # Nếu Editor xử lý phím (1, 2, M, S) thì bỏ qua các xử lý game phía dưới
                if self.editor.handle_keydown(event.key):
                    continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Nếu Editor xử lý click chuột trái/phải trên bản đồ thì bỏ qua xử lý bên dưới
                if self.editor.handle_mouse_click(event.pos, event.button):
                    continue
            
            # Khóa các tương tác chạy game bình thường nếu Map Editor đang bật
            if self.editor.active:
                continue
            
            if self.model.game_won:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    if self.view.again_btn and self.view.again_btn.collidepoint(mouse_pos):
                        self.model.reset()
                        self.is_tracking_move = False
                    elif self.view.next_btn and self.view.next_btn.collidepoint(mouse_pos):
                        has_next = self.model.load_next_map()
                        if has_next:
                            self.view.update_screen_size(len(self.model.matrix), len(self.model.matrix[0]))
                            self.is_tracking_move = False
                            pygame.event.clear()
                            return 
            else:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    
                    if self.view.reset_button and self.view.reset_button.collidepoint(mouse_pos):
                        if self.is_tracking_move and self.start_move_time:
                            self.model.update_last_record_run_time(time.perf_counter() - self.start_move_time, is_cancelled=True)
                        self.model.reset()
                        self.is_tracking_move = False
                        continue
                        
                    if self.view.history_button and self.view.history_button.collidepoint(mouse_pos):
                        self.model.show_history = True
                        continue
                    
                    if not self.model.moving:
                        clicked_algo = None
                        for name, box in self.view.algo_buttons.items():
                            if box.collidepoint(mouse_pos):
                                clicked_algo = name
                                break
                        
                        if clicked_algo:
                            path, visited, max_q = [], 0, 0
                            current_pos = self.model.knight_pos
                            
                            start_ticks = time.perf_counter()
                            if clicked_algo == "BFS": path, visited, max_q = BFS(self.model.matrix, current_pos, self.model.end_pos)
                            elif clicked_algo == "DFS": path, visited, max_q = DFS(self.model.matrix, current_pos, self.model.end_pos)
                            elif clicked_algo == "UCS": path, visited, max_q = UCS(self.model.matrix, current_pos, self.model.end_pos)
                            elif clicked_algo == "Greedy": path, visited, max_q = Greedy(self.model.matrix, current_pos, self.model.end_pos)
                            elif clicked_algo == "A*": path, visited, max_q = Astar(self.model.matrix, current_pos, self.model.end_pos)
                            end_ticks = time.perf_counter()
                            
                            exec_time = (end_ticks - start_ticks) * 1000
                            
                            if path:
                                self.model.active_algo = clicked_algo
                                self.model.set_path(path)
                                self.model.add_history_record(clicked_algo, exec_time, self.model.path_cost, len(path) - 1, visited, max_q)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        if self.is_tracking_move and self.start_move_time:
                            self.model.update_last_record_run_time(time.perf_counter() - self.start_move_time, is_cancelled=True)
                        self.model.reset()
                        self.is_tracking_move = False
                        continue 

                    if not self.model.moving:
                        if event.key == pygame.K_UP: self.model.move_manual(-1, 0)
                        elif event.key == pygame.K_DOWN: self.model.move_manual(1, 0)
                        elif event.key == pygame.K_LEFT: self.model.move_manual(0, -1)
                        elif event.key == pygame.K_RIGHT: self.model.move_manual(0, 1)
                        if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                            continue

                    if self.model.moving: 
                        continue
                    
                    path, visited, max_q = [], 0, 0
                    current_pos = self.model.knight_pos
                    algo_name = ""

                    start_ticks = time.perf_counter()
                    if event.key == pygame.K_b: path, visited, max_q = BFS(self.model.matrix, current_pos, self.model.end_pos); algo_name = "BFS"
                    elif event.key == pygame.K_d: path, visited, max_q = DFS(self.model.matrix, current_pos, self.model.end_pos); algo_name = "DFS"
                    elif event.key == pygame.K_u: path, visited, max_q = UCS(self.model.matrix, current_pos, self.model.end_pos); algo_name = "UCS"
                    elif event.key == pygame.K_g: path, visited, max_q = Greedy(self.model.matrix, current_pos, self.model.end_pos); algo_name = "Greedy"
                    elif event.key == pygame.K_a: path, visited, max_q = Astar(self.model.matrix, current_pos, self.model.end_pos); algo_name = "A*"
                    end_ticks = time.perf_counter()
                    
                    exec_time = (end_ticks - start_ticks) * 1000
                    
                    if path and algo_name != "":
                        self.model.active_algo = algo_name
                        self.model.set_path(path)
                        self.model.add_history_record(algo_name, exec_time, self.model.path_cost, len(path) - 1, visited, max_q)