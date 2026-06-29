"""
editmap.py
----------
Module quản lý chức năng CHỈNH SỬA BẢN ĐỒ (Map Editor) trong lúc chơi game.

Quy tắc hoạt động:
  - Bấm phím [E]            : Toggle vào / ra chế độ Edit Map.
  - (Trong chế độ Edit)
      + Click CHUỘT PHẢI vào 1 ô  -> Xóa ô đó, trả về thành Đất bằng '0' (chi phí 1).
      + Click CHUỘT TRÁI vào 1 ô  -> Chọn ô đó (highlight), chưa đổi gì cả.
      + Sau khi đã chọn 1 ô, bấm:
            phím [1] -> đổi ô đang chọn thành Tường       ('1', không đi qua được)
            phím [2] -> đổi ô đang chọn thành Đầm lầy      ('2', chi phí 5)
            phím [M] -> đổi ô đang chọn thành Vùng quái    ('M', chi phí 50)
      + Bấm phím [S] -> Lưu map hiện tại ra file txt (ghi đè lên file map đang chơi).

Ràng buộc an toàn:
  - Không cho phép edit lên ô Hiệp sĩ (start_pos) hoặc Công chúa (end_pos),
    để tránh làm hỏng cấu trúc map (mất điểm xuất phát / đích).
  - Không cho chỉnh sửa map khi Hiệp sĩ đang di chuyển (model.moving) hoặc khi đã thắng (game_won),
    để tránh xung đột trạng thái giữa việc edit và việc chạy thuật toán / di chuyển.
"""

import pygame
from view import MAP_OFFSET_X


class MapEditor:
    # Các ô không được phép edit (an toàn cấu trúc map)
    PROTECTED_CHARS = ('K', 'P')

    # Ánh xạ phím bấm -> ký hiệu địa hình mới
    KEY_TO_TERRAIN = {
        pygame.K_1: '1',   # Tường
        pygame.K_2: '2',   # Đầm lầy
        pygame.K_m: 'M',   # Quái vật
    }

    TERRAIN_NAME = {'1': 'Tường', '2': 'Đầm lầy', 'M': 'Quái vật'}

    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.active = False          # Đang ở chế độ Edit Map hay không
        self.selected_cell = None    # Tọa độ (r, c) ô đang được chọn bằng chuột trái
        self.message = ""            # Thông báo ngắn hiển thị trên màn hình (ví dụ: "Đã lưu map!")
        self.message_timer = 0       # Mốc thời gian (ticks) mà message sẽ hết hạn hiển thị

    # ------------------------------------------------------------------
    # TOGGLE BẬT / TẮT CHẾ ĐỘ EDIT
    # ------------------------------------------------------------------
    def toggle(self):
        """ Bật / tắt chế độ Edit Map. Không cho bật khi Hiệp sĩ đang di chuyển hoặc đã thắng. """
        if self.model.moving or self.model.game_won:
            self._set_message("Không thể chỉnh sửa khi đang chạy hoặc đã thắng!")
            return

        self.active = not self.active
        self.selected_cell = None  # Mỗi lần toggle thì bỏ chọn ô cũ

        if self.active:
            self._set_message("Đã vào chế độ EDIT MAP (Nhấn E để thoát)")
        else:
            self._set_message("Đã thoát chế độ Edit Map")

    # ------------------------------------------------------------------
    # XỬ LÝ TỌA ĐỘ MÀN HÌNH -> TỌA ĐỘ Ô TRONG MA TRẬN
    # ------------------------------------------------------------------
    def screen_to_cell(self, mouse_pos):
        """
        Chuyển tọa độ pixel chuột (x, y) thành tọa độ ô (r, c) trong matrix.
        Trả về None nếu click ra ngoài vùng bản đồ (ví dụ: click vào banner trái/phải).
        """
        mx, my = mouse_pos
        tile = self.view.TILE_SIZE

        local_x = mx - MAP_OFFSET_X
        local_y = my - self.view.MAP_OFFSET_Y

        if local_x < 0 or local_y < 0:
            return None

        c = local_x // tile
        r = local_y // tile

        rows = len(self.model.matrix)
        cols = len(self.model.matrix[0])

        if 0 <= r < rows and 0 <= c < cols:
            return (int(r), int(c))
        return None

    # ------------------------------------------------------------------
    # XỬ LÝ CLICK CHUỘT
    # ------------------------------------------------------------------
    def handle_mouse_click(self, mouse_pos, button):
        """
        button: 1 = chuột trái, 3 = chuột phải (theo chuẩn pygame.MOUSEBUTTONDOWN.button)
        Trả về True nếu Editor đã xử lý click này (để Controller không xử lý trùng các nút khác).
        """
        if not self.active:
            return False

        cell = self.screen_to_cell(mouse_pos)
        if cell is None:
            return False  # Click ngoài vùng map (banner...), để Controller xử lý (ví dụ nút Reset)

        r, c = cell

        # Không cho edit lên ô Hiệp sĩ / Công chúa để giữ an toàn cấu trúc map
        if self.model.matrix[r][c] in self.PROTECTED_CHARS:
            self._set_message("Không thể chỉnh sửa ô Hiệp sĩ / Công chúa!")
            return True

        if button == 3:
            # CHUỘT PHẢI -> Xóa ô, trả về Đất bằng '0'
            self.model.matrix[r][c] = '0'
            if self.selected_cell == (r, c):
                self.selected_cell = None
            self._set_message(f"Đã xóa ô ({r},{c}) -> Đất bằng")

        elif button == 1:
            # CHUỘT TRÁI -> Chọn ô để chuẩn bị đổi địa hình bằng phím số
            self.selected_cell = (r, c)
            self._set_message(f"Đã chọn ô ({r},{c}). Nhấn [1]=Tường [2]=Đầm lầy [M]=Quái")

        return True

    # ------------------------------------------------------------------
    # XỬ LÝ BÀN PHÍM (đổi địa hình ô đang chọn + lưu map)
    # ------------------------------------------------------------------
    def handle_keydown(self, key):
        """ Trả về True nếu phím đã được Editor xử lý (để Controller không xử lý trùng) """
        if not self.active:
            return False

        # Phím S -> Lưu map ra file (hoạt động bất kể có ô đang chọn hay không)
        if key == pygame.K_s:
            saved_path = self.model.save_map()
            filename = saved_path.replace('\\', '/').split('/')[-1]
            self._set_message(f"Đã lưu map vào file: {filename}")
            return True

        # Các phím 1 / 2 / M -> đổi địa hình ô đang được chọn bằng chuột trái
        if key in self.KEY_TO_TERRAIN:
            if self.selected_cell is None:
                self._set_message("Hãy click chuột trái để chọn 1 ô trước!")
                return True

            r, c = self.selected_cell
            new_terrain = self.KEY_TO_TERRAIN[key]
            self.model.matrix[r][c] = new_terrain

            terrain_name = self.TERRAIN_NAME[new_terrain]
            self._set_message(f"Ô ({r},{c}) -> {terrain_name}")
            return True

        return False

    # ------------------------------------------------------------------
    # THÔNG BÁO TẠM THỜI (hiện vài giây rồi tự ẩn)
    # ------------------------------------------------------------------
    def _set_message(self, text, duration_ms=2200):
        self.message = text
        self.message_timer = pygame.time.get_ticks() + duration_ms

    def get_active_message(self):
        """ Trả về message nếu còn trong thời gian hiển thị, ngược lại trả về chuỗi rỗng """
        if self.message and pygame.time.get_ticks() < self.message_timer:
            return self.message
        return ""