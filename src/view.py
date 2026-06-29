import pygame
import os
import math

pg = pygame
BANNER_WIDTH = 230
MAP_OFFSET_X = BANNER_WIDTH

class AnimatedSprite:
    def __init__(self, image_path, num_frames, fps=5, tile_size=48):
        self.tile_size = tile_size
        self.num_frames = num_frames
        self.frames = []
        try:
            self.sheet = pygame.image.load(image_path).convert_alpha()
            self.frame_width = self.sheet.get_width() // self.num_frames
            self.frame_height = self.sheet.get_height()
            for i in range(self.num_frames):
                sub = self.sheet.subsurface((i * self.frame_width, 0, self.frame_width, self.frame_height))
                scaled = pygame.transform.smoothscale(sub, (self.tile_size, self.tile_size))
                self.frames.append(scaled)
            self.has_image = True
        except Exception as e:
            print(f"[CẢNH BÁO] Không tìm thấy asset: {image_path}. Lỗi: {e}")
            self.has_image = False
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_delay = 1000 // fps

    def update(self):
        if not self.has_image: return
        now = pygame.time.get_ticks()
        if now - self.last_update >= self.frame_delay:
            self.current_frame = (self.current_frame + 1) % self.num_frames
            self.last_update = now

    def get_frame(self):
        if not self.has_image or not self.frames: return None
        return self.frames[self.current_frame]


class MazeView:
    TILE_SIZE = 48

    C_BG_DARK    = (10,  12,  24)   
    C_ACCENT2    = (246, 173, 85) 
    C_GREEN      = (46,  204, 113)
    C_BTN_ACTIVE = (60,  100, 180)


    FALLBACK_COLORS = {
        '1': (55,  55,  70),
        '0': (30,  100, 40),
        '2': (70,  50,  25),
        'M': (100, 20,  20),
        'P': (220, 80,  180),
        'PATH_LINE': (46, 204, 113),
    }

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        
        self.algo_buttons = {}
        self.reset_button = None
        self.history_button = None 
        self.close_history_btn = None 
        self.edit_switch_rect = None # Vùng va chạm của nút Edit Map

        self.current_algo_name = "None"
        self.current_step_index = 0
        self.total_path_steps = 0
        self.total_path_cost = 0

        self._rebuild_screen()
        pygame.display.set_caption("Giai Cuu Cong Chua")

        self.again_btn  = None
        self.next_btn   = None
        self.animation_frame = 0

        base_dir   = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(base_dir, 'assets')

        self.assets = {}
        self.load_static_tile(assets_dir, '1', 'wall.png')
        self.load_static_tile(assets_dir, '0', 'grass.png')
        self.load_static_tile(assets_dir, '2', 'swamp.png')

        self.princess_img = None
        p_path = os.path.join(assets_dir, 'princess.png')
        if os.path.exists(p_path):
            try:
                img = pygame.image.load(p_path).convert_alpha()
                self.princess_img = pygame.transform.scale(img, (self.TILE_SIZE, self.TILE_SIZE))
            except Exception: pass

        self.knight_anim  = AnimatedSprite(os.path.join(assets_dir, 'knight_spritesheet.png'), num_frames=3, fps=6, tile_size=self.TILE_SIZE)
        self.monster_anim = AnimatedSprite(os.path.join(assets_dir, 'monster_area.png'),       num_frames=2, fps=4, tile_size=self.TILE_SIZE)

    def _rebuild_screen(self):
        self.map_width_pixels = self.cols * self.TILE_SIZE
        map_h = self.rows * self.TILE_SIZE
        
        total_w = BANNER_WIDTH * 2 + self.map_width_pixels
        self.total_screen_height = max(map_h, 640) # Đảm bảo đủ chiều cao chứa thêm nút mới trong banner
        
        self.MAP_OFFSET_Y = (self.total_screen_height - map_h) // 2

        self.screen = pygame.display.set_mode((total_w, self.total_screen_height))
        self.surface = self.screen  

    def load_static_tile(self, assets_dir, key, filename):
        path = os.path.join(assets_dir, filename)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                self.assets[key] = pygame.transform.scale(img, (self.TILE_SIZE, self.TILE_SIZE))
                return
            except Exception: pass
        self.assets[key] = None

    def update_screen_size(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self._rebuild_screen()
        pygame.display.flip()

    def render(self, model, editor=None): 
        self.animation_frame += 1
        self.knight_anim.update()
        self.monster_anim.update()

        self.current_step_index = model.path_index if model.path else 0
        self.total_path_steps = max(0, len(model.path) - 1) if model.path else 0
        self.total_path_cost = model.path_cost if hasattr(model, 'path_cost') else 0
        self.current_algo_name = getattr(model, 'active_algo', 'None')

        self.screen.fill(self.C_BG_DARK)

        # Vẽ các thành phần nền
        self.draw_info_banner()
        self._draw_map(model)
        self._draw_path(model)
        self._draw_princess(model)
        self._draw_knight(model)
        
        # Truyền trạng thái editor vào trực tiếp hàm vẽ banner thuật toán
        editor_active = editor.active if editor else False
        self.draw_algo_banner(editor_active)

        # --- PHẦN HIỂN THỊ ĐỒ HỌA CHO CHẾ ĐỘ EDIT MAP ---
        if editor and editor.active:
            if editor.selected_cell:
                r, c = editor.selected_cell
                rect = pygame.Rect(MAP_OFFSET_X + c * self.TILE_SIZE, 
                                   self.MAP_OFFSET_Y + r * self.TILE_SIZE, 
                                   self.TILE_SIZE, self.TILE_SIZE)
                pygame.draw.rect(self.screen, (255, 140, 0), rect, width=3)

            msg = editor.get_active_message()
            if msg:
                font_msg = pygame.font.SysFont("Segoe UI", 13, bold=True)
                msg_surf = font_msg.render(msg, True, (255, 235, 59))
                
                bg_rect = pygame.Rect(MAP_OFFSET_X + 10, self.total_screen_height - 35, 
                                      self.map_width_pixels - 20, 26)
                pygame.draw.rect(self.screen, (20, 20, 30), bg_rect, border_radius=4)
                pygame.draw.rect(self.screen, (255, 140, 0), bg_rect, width=1, border_radius=4)
                
                self.screen.blit(msg_surf, msg_surf.get_rect(center=bg_rect.center))
        # ------------------------------------------------

        if model.game_won:
            
            self._render_victory_popup()

        if model.show_history:
            self._render_history_overlay(model)

        pygame.display.flip()

    def _draw_map(self, model):
        matrix = model.matrix
        for r in range(self.rows):
            for c in range(self.cols):
                tt = matrix[r][c]
                rect = pygame.Rect(MAP_OFFSET_X + c * self.TILE_SIZE, 
                                   self.MAP_OFFSET_Y + r * self.TILE_SIZE, 
                                   self.TILE_SIZE, self.TILE_SIZE)
                base_key = tt if tt in ['1', '0', '2'] else '0'
                if self.assets.get(base_key):
                    self.screen.blit(self.assets[base_key], rect)
                else:
                    pygame.draw.rect(self.screen, self.FALLBACK_COLORS.get(base_key, (0,0,0)), rect)
                if tt == 'M':
                    m_frame = self.monster_anim.get_frame()
                    if m_frame:
                        self.screen.blit(m_frame, rect)
                    else:
                        pygame.draw.rect(self.screen, self.FALLBACK_COLORS['M'], rect)

    def _draw_path(self, model):
        if model.path:
            for idx, (r, c) in enumerate(model.path[1:-1]):
                cx = MAP_OFFSET_X + c * self.TILE_SIZE + self.TILE_SIZE // 2
                cy = self.MAP_OFFSET_Y + r * self.TILE_SIZE + self.TILE_SIZE // 2
                pygame.draw.circle(self.screen, self.FALLBACK_COLORS['PATH_LINE'], (cx, cy), self.TILE_SIZE // 6)

    def _draw_princess(self, model):
        p_r, p_c = model.end_pos
        px = MAP_OFFSET_X + p_c * self.TILE_SIZE
        py = self.MAP_OFFSET_Y + p_r * self.TILE_SIZE
        bob  = math.sin(self.animation_frame * 0.13) * 5
        sway = math.sin(self.animation_frame * 0.1)  * 3
        if self.princess_img:
            glow = pygame.Surface((self.TILE_SIZE + 20, self.TILE_SIZE + 20), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 180, 240, 55),
                               (self.TILE_SIZE//2 + 10, self.TILE_SIZE//2 + 10 + int(bob)),
                               self.TILE_SIZE//2 + 8)
            self.screen.blit(glow, (px - 10, py - 10 + int(bob)))
            rotated = pygame.transform.rotozoom(self.princess_img, sway * 0.4, 1.0)
            nr = rotated.get_rect(center=(px + self.TILE_SIZE//2, int(py + self.TILE_SIZE//2 + bob)))
            self.screen.blit(rotated, nr)
        else:
            pygame.draw.polygon(self.screen, self.FALLBACK_COLORS['P'],
                                [(px+10, py+25+int(bob)), (px+24, py+45+int(bob)), (px+38, py+25+int(bob))])

    def _draw_knight(self, model):
        k_r, k_c = model.knight_pos
        kx = MAP_OFFSET_X + k_c * self.TILE_SIZE
        ky = self.MAP_OFFSET_Y + k_r * self.TILE_SIZE
        k_frame = self.knight_anim.get_frame()
        if k_frame:
            glow = pygame.Surface((self.TILE_SIZE + 20, self.TILE_SIZE + 20), pygame.SRCALPHA)
            pygame.draw.circle(glow, (100, 180, 255, 40),
                               (self.TILE_SIZE//2 + 10, self.TILE_SIZE//2 + 10), self.TILE_SIZE//2 + 8)
            self.screen.blit(glow, (kx - 10, ky - 10))
            self.screen.blit(k_frame, (kx, ky))
        else:
            pygame.draw.rect(self.screen, (52, 152, 219), (kx, ky, self.TILE_SIZE, self.TILE_SIZE))

    def draw_info_banner(self):
        margin = 12
        banner_w = BANNER_WIDTH - (margin * 2)
        banner_h = 490
        
        outer_rect = pg.Rect(margin, margin, banner_w, banner_h)
        pg.draw.rect(self.surface, (30, 34, 42), outer_rect, border_radius=18)
        pg.draw.rect(self.surface, (212, 175, 55), outer_rect, width=3, border_radius=18)
        
        title_font = pg.font.SysFont("Segoe UI", 16, bold=True)
        content_font = pg.font.SysFont("Segoe UI", 14, bold=True)
        text_font = pg.font.SysFont("Segoe UI", 14)
        
        inner_w = banner_w - 20
        inner_h_top = 200
        inner_h_bottom = 250
        
        rect_top = pg.Rect(margin + 10, margin + 12, inner_w, inner_h_top)
        pg.draw.rect(self.surface, (23, 26, 33), rect_top, border_radius=12)
        pg.draw.rect(self.surface, (73, 80, 87), rect_top, width=2, border_radius=12)
        
        y_offset_top = rect_top.y + 20
        x_padding = rect_top.x + 15
        
        txt_project = title_font.render("THÔNG TIN DỰ ÁN", True, (255, 215, 0))
        self.surface.blit(txt_project, (x_padding, y_offset_top))
        y_offset_top += 40
        
        txt_group_label = content_font.render("Số nhóm:", True, (173, 181, 189))
        txt_group_val = text_font.render("Nhóm 09", True, (255, 255, 255))
        self.surface.blit(txt_group_label, (x_padding, y_offset_top))
        self.surface.blit(txt_group_val, (x_padding + 75, y_offset_top))
        y_offset_top += 35
        
        txt_topic_label = content_font.render("Tên đề tài:", True, (173, 181, 189))
        self.surface.blit(txt_topic_label, (x_padding, y_offset_top))
        y_offset_top += 25
        
        txt_title1 = text_font.render("Game Giải Cứu Công Chúa", True, (0, 255, 127))
        txt_title2 = text_font.render("(Pygame Graph Search)", True, (0, 255, 127))
        self.surface.blit(txt_title1, (x_padding, y_offset_top))
        y_offset_top += 22
        self.surface.blit(txt_title2, (x_padding, y_offset_top))
        
        rect_bottom = pg.Rect(margin + 10, rect_top.bottom + 15, inner_w, inner_h_bottom)
        pg.draw.rect(self.surface, (23, 26, 33), rect_bottom, border_radius=12)
        pg.draw.rect(self.surface, (73, 80, 87), rect_bottom, width=2, border_radius=12)
        
        y_offset_bot = rect_bottom.y + 20
        
        txt_member_title = title_font.render("THÀNH VIÊN NHÓM", True, (255, 215, 0))
        self.surface.blit(txt_member_title, (x_padding, y_offset_bot))
        y_offset_bot += 40
        
        members = [
            ("Lê Quang Hưng", "MSSV: 24110230"),
            ("Lê văn Hoàng", "MSSV: 24110218"),
            ("Võ Đỗ Hoàng Việt", "MSSV: 24110382")
        ]
        
        for name, mssv in members:
            name_surf = content_font.render(f"• {name}", True, (255, 255, 255))
            mssv_surf = text_font.render(mssv, True, (206, 212, 218))
            
            self.surface.blit(name_surf, (x_padding, y_offset_bot))
            y_offset_bot += 22
            self.surface.blit(mssv_surf, (x_padding + 12, y_offset_bot))
            y_offset_bot += 30

    def draw_algo_banner(self, editor_active=False):
        margin = 12
        banner_x = MAP_OFFSET_X + self.map_width_pixels + margin
        banner_w = BANNER_WIDTH - (margin * 2)
        banner_h = self.total_screen_height - (margin * 2)
        
        outer_rect = pg.Rect(banner_x, margin, banner_w, banner_h)
        pg.draw.rect(self.surface, (16, 20, 36), outer_rect, border_radius=18)
        pg.draw.rect(self.surface, (44, 76, 133), outer_rect, width=2, border_radius=18)
        
        title_font = pg.font.SysFont("Segoe UI", 16, bold=True)
        algo_text_font = pg.font.SysFont("Segoe UI", 14, bold=True)
        key_hint_font = pg.font.SysFont("Segoe UI", 11, bold=True)
        content_font = pg.font.SysFont("Segoe UI", 14)
        number_font = pg.font.SysFont("Segoe UI", 26, bold=True)
        btn_font = pg.font.SysFont("Segoe UI", 13, bold=True)
        
        y_offset = margin + 15
        x_padding = banner_x + 15
        box_width = banner_w - 30

        # --- PHẦN DANH SÁCH THUẬT TOÁN ---
        txt_algos_header = title_font.render("ALGORITHMS", True, (77, 166, 255))
        self.surface.blit(txt_algos_header, (x_padding, y_offset))
        y_offset += 25
        
        algorithms = [
            ("BFS", "B"), ("DFS", "D"), ("UCS", "U"), ("Greedy", "G"), ("A*", "A")
        ]
        
        for name, key in algorithms:
            algo_box = pg.Rect(x_padding, y_offset, box_width, 32)
            self.algo_buttons[name] = algo_box 
            
            if self.current_algo_name == name:
                pg.draw.rect(self.surface, (44, 100, 180), algo_box, border_radius=6)
            else:
                pg.draw.rect(self.surface, (25, 33, 56), algo_box, border_radius=6)
            pg.draw.rect(self.surface, (38, 54, 92), algo_box, width=1, border_radius=6)
            
            name_surf = algo_text_font.render(name, True, (175, 195, 230))
            self.surface.blit(name_surf, (algo_box.x + 12, algo_box.y + 6))
            
            key_box = pg.Rect(algo_box.right - 28, algo_box.y + 6, 18, 20)
            pg.draw.rect(self.surface, (38, 58, 97), key_box, border_radius=4)
            key_surf = key_hint_font.render(key, True, (92, 148, 232))
            self.surface.blit(key_surf, key_surf.get_rect(center=key_box.center))
            
            y_offset += 38
        
        y_offset += 5
        pg.draw.line(self.surface, (30, 43, 74), (x_padding, y_offset), (banner_x + banner_w - 15, y_offset), 1)
        y_offset += 10

        # --- PHẦN THÔNG SỐ BƯỚC ĐI ---
        txt_steps_header = title_font.render("STEPS & COST", True, (77, 166, 255))
        self.surface.blit(txt_steps_header, (x_padding, y_offset))
        y_offset += 22
        
        step_val_surf = number_font.render(str(self.current_step_index), True, (241, 154, 62))
        self.surface.blit(step_val_surf, (banner_x + banner_w // 2 - step_val_surf.get_width() // 2, y_offset))
        y_offset += 30
        
        total_steps_surf = content_font.render(f"/ {self.total_path_steps} total ({self.current_algo_name})", True, (140, 160, 200))
        self.surface.blit(total_steps_surf, (banner_x + banner_w // 2 - total_steps_surf.get_width() // 2, y_offset))
        y_offset += 22
        
        progress_bg = pg.Rect(x_padding, y_offset, box_width, 4)
        pg.draw.rect(self.surface, (25, 33, 56), progress_bg)
        if self.total_path_steps > 0:
            fill_width = int(box_width * (self.current_step_index / self.total_path_steps))
            if fill_width > 0:
                pg.draw.rect(self.surface, (241, 154, 62), pg.Rect(x_padding, y_offset, fill_width, 4))
        
        y_offset += 12
        cost_surf = content_font.render(f"Cost: {self.total_path_cost}", True, (138, 158, 199))
        self.surface.blit(cost_surf, (banner_x + banner_w // 2 - cost_surf.get_width() // 2, y_offset))
        y_offset += 20
        
        lbl_cost_info1 = key_hint_font.render("Rules: Land: 1 | Swamp: 5", True, (85, 105, 145))
        lbl_cost_info2 = key_hint_font.render("Monster: 50 / 1 cell", True, (190, 85, 85))
        self.surface.blit(lbl_cost_info1, (banner_x + banner_w // 2 - lbl_cost_info1.get_width() // 2, y_offset))
        y_offset += 14
        self.surface.blit(lbl_cost_info2, (banner_x + banner_w // 2 - lbl_cost_info2.get_width() // 2, y_offset))
        
        y_offset += 15
        pg.draw.line(self.surface, (30, 43, 74), (x_padding, y_offset), (banner_x + banner_w - 15, y_offset), 1)
        y_offset += 10

        # --- PHẦN ĐIỀU KHIỂN (CONTROLS) ---
        txt_controls_header = title_font.render("CONTROLS", True, (77, 166, 255))
        self.surface.blit(txt_controls_header, (x_padding, y_offset))
        y_offset += 25
        
        # NÚT 1: RESET BUTTON
        self.reset_button = pg.Rect(x_padding, y_offset, box_width, 32)
        pg.draw.rect(self.surface, (186, 45, 59), self.reset_button, border_radius=6)
        txt_reset = btn_font.render("RESET  [R]", True, (255, 255, 255))
        self.surface.blit(txt_reset, txt_reset.get_rect(center=self.reset_button.center))
        y_offset += 38

        # NÚT 2: HISTORY BUTTON
        self.history_button = pg.Rect(x_padding, y_offset, box_width, 32)
        pg.draw.rect(self.surface, (44, 120, 110), self.history_button, border_radius=6)
        txt_history = btn_font.render("LỊCH SỬ THUẬT TOÁN", True, (255, 255, 255))
        self.surface.blit(txt_history, txt_history.get_rect(center=self.history_button.center))
        y_offset += 38

        # NÚT 3: EDIT MAP BUTTON (MỚI CHUYỂN VÀO ĐÂY)
        self.edit_switch_rect = pg.Rect(x_padding, y_offset, box_width, 32)
        # Thay đổi màu nền nút tùy thuộc vào trạng thái Active (Xanh lá / Xám xanh đen)
        edit_bg_color = (46, 204, 113) if editor_active else (50, 60, 85)
        pg.draw.rect(self.surface, edit_bg_color, self.edit_switch_rect, border_radius=6)
        pg.draw.rect(self.surface, (70, 90, 130), self.edit_switch_rect, width=1, border_radius=6)
        
        edit_text = f"EDIT MAP: {'ON' if editor_active else 'OFF'} [E]"
        txt_edit = btn_font.render(edit_text, True, (255, 255, 255))
        self.surface.blit(txt_edit, txt_edit.get_rect(center=self.edit_switch_rect.center))
        y_offset += 35
        
        txt_hint = key_hint_font.render("Press key to run algo", True, (65, 82, 117))
        self.surface.blit(txt_hint, (banner_x + banner_w // 2 - txt_hint.get_width() // 2, y_offset))

    def _render_victory_popup(self):
        sw = self.screen.get_width()
        sh = self.screen.get_height()
        box_w, box_h = 340, 170
        bx = (sw - box_w) // 2
        by = (sh - box_h) // 2

        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        font_win = pygame.font.SysFont('Arial', 28, bold=True)
        font_winbtn = pygame.font.SysFont('Arial', 16, bold=True)

        box = pygame.Rect(bx, by, box_w, box_h)
        pygame.draw.rect(self.screen, (30, 34, 60), box, border_radius=12)
        pygame.draw.rect(self.screen, self.C_ACCENT2, box, 3, border_radius=12)

        title = font_win.render("VICTORY!", True, self.C_ACCENT2)
        self.screen.blit(title, (bx + (box_w - title.get_width())//2, by + 18))

        self.again_btn = pygame.Rect(bx + 30,         by + 95, 130, 44)
        self.next_btn  = pygame.Rect(bx + box_w - 160, by + 95, 130, 44)

        pygame.draw.rect(self.screen, self.C_GREEN,   self.again_btn, border_radius=8)
        pygame.draw.rect(self.screen, self.C_BTN_ACTIVE, self.next_btn, border_radius=8)

        a_lbl = font_winbtn.render("Again", True, (0, 0, 0))
        n_lbl = font_winbtn.render("Next >",   True, (255, 255, 255))

        self.screen.blit(a_lbl, (self.again_btn.x + (130 - a_lbl.get_width())//2,
                                  self.again_btn.y + (44  - a_lbl.get_height())//2))
        self.screen.blit(n_lbl, (self.next_btn.x  + (130 - n_lbl.get_width())//2,
                                  self.next_btn.y  + (44  - n_lbl.get_height())//2))

    def _render_history_overlay(self, model):
        sw = self.screen.get_width()
        sh = self.screen.get_height()
        
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((12, 15, 28, 245))
        self.screen.blit(overlay, (0, 0))
        
        box_w, box_h = max(820, sw - 40), max(420, sh - 80)
        bx = (sw - box_w) // 2
        by = (sh - box_h) // 2
        
        box_rect = pygame.Rect(bx, by, box_w, box_h)
        pygame.draw.rect(self.screen, (20, 24, 42), box_rect, border_radius=16)
        pygame.draw.rect(self.screen, (77, 166, 255), box_rect, width=2, border_radius=16)
        
        title_font = pygame.font.SysFont("Segoe UI", 22, bold=True)
        header_font = pygame.font.SysFont("Segoe UI", 12, bold=True)
        data_font = pygame.font.SysFont("Segoe UI", 12)
        
        title_surf = title_font.render("BÁO CÁO PHÂN TÍCH HIỆU SUẤT AI QUÉT ĐƯỜNG", True, (255, 215, 0))
        self.screen.blit(title_surf, (bx + 25, by + 20))
        
        headers = [
            ("STT", bx + 20), ("Thuật toán", bx + 65), ("Node đã duyệt", bx + 160),
            ("Node còn lại", bx + 265), ("Hiệu suất hướng đích", bx + 370),
            ("Tổng bước", bx + 505), ("Chi phí", bx + 585), ("Thời gian dò", bx + 645),
            ("Thời gian chạy", bx + 745)
        ]
        
        header_bar = pygame.Rect(bx + 12, by + 65, box_w - 24, 30)
        pygame.draw.rect(self.screen, (30, 37, 64), header_bar, border_radius=4)
        for text, x in headers:
            h_surf = header_font.render(text, True, (135, 206, 250))
            self.screen.blit(h_surf, (x, by + 72))
            
        y_pos = by + 105
        max_visible_y = by + box_h - 60
        
        if not model.history_log:
            empty_surf = data_font.render("Chưa ghi nhận dữ liệu phân tích thuật toán nào.", True, (140, 155, 200))
            self.screen.blit(empty_surf, (bx + 30, y_pos + 10))
        else:
            for idx, record in enumerate(model.history_log):
                if y_pos > max_visible_y: 
                    break
                
                row_rect = pygame.Rect(bx + 12, y_pos, box_w - 24, 26)
                if idx % 2 == 0:
                    pygame.draw.rect(self.screen, (25, 30, 52), row_rect, border_radius=4)
                
                stt_s = data_font.render(f"{idx + 1:02d}", True, (140, 155, 200))
                name_s = header_font.render(record['name'], True, (0, 255, 127))
                visited_s = data_font.render(str(record.get('visited', 0)), True, (240, 240, 240))
                max_q_s = data_font.render(str(record.get('max_queue', 0)), True, (200, 220, 255))
                
                eff = record.get('efficiency', 0.0)
                eff_s = data_font.render(f"{eff:.1f}%", True, (100, 255, 100) if eff > 50 else (255, 150, 150))
                
                steps_s = data_font.render(str(record['steps']), True, (99, 179, 237))
                cost_s = data_font.render(str(record['cost']), True, (246, 173, 85))
                
                s_time = record.get('search_time', 0.0)
                s_time_str = f"{s_time:.4f} ms" if s_time >= 0.0001 else "< 0.0001 ms"
                search_time_s = data_font.render(s_time_str, True, (220, 220, 220))
                
                r_time = record.get('run_time', 0.0)
                status = record.get('status', 'Đang đi...')
                
                if status == 'Bị hủy':
                    run_time_str = "Bị hủy (R)"
                    r_color = (255, 90, 90)
                elif model.moving and idx == len(model.history_log) - 1 and not model.game_won:
                    run_time_str = "Đang đi..."
                    r_color = (240, 240, 100)
                else:
                    run_time_str = f"{r_time:.2f} s"
                    r_color = (255, 255, 255)
                    
                run_time_s = data_font.render(run_time_str, True, r_color)
                
                self.screen.blit(stt_s, (bx + 20, y_pos + 4))
                self.screen.blit(name_s, (bx + 65, y_pos + 4))
                self.screen.blit(visited_s, (bx + 160, y_pos + 4))
                self.screen.blit(max_q_s, (bx + 265, y_pos + 4))
                self.screen.blit(eff_s, (bx + 370, y_pos + 4))
                self.screen.blit(steps_s, (bx + 505, y_pos + 4))
                self.screen.blit(cost_s, (bx + 585, y_pos + 4))
                self.screen.blit(search_time_s, (bx + 645, y_pos + 4))
                self.screen.blit(run_time_s, (bx + 745, y_pos + 4))
                
                y_pos += 30
                
        self.close_history_btn = pygame.Rect(bx + box_w - 120, by + box_h - 45, 100, 32)
        pygame.draw.rect(self.screen, (190, 45, 55), self.close_history_btn, border_radius=6)
        close_lbl = header_font.render("Đóng [X]", True, (255, 255, 255))
        self.screen.blit(close_lbl, close_lbl.get_rect(center=self.close_history_btn.center))