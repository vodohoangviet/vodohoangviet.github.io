import pygame
from model import MazeModel
from view import MazeView
from controller import GameController

def main():
    pygame.init()
    
    # 1. Khởi tạo dữ liệu từ map
    model = MazeModel()
    
    # 2. Khởi tạo giao diện dựa trên kích thước của map
    rows = len(model.matrix)
    cols = len(model.matrix[0])
    view = MazeView(rows, cols)
    
    # 3. Giao cho bộ điều khiển quản lý và chạy game
    controller = GameController(model, view)
    controller.run()

if __name__ == "__main__":
    main()