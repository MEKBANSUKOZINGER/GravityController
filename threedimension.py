import pygame
import math
import sys
import random

# 초기 설정
pygame.init()
WIDTH, HEIGHT = 800, 600  # 창 크기
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (50, 20, 128)
DARK_PURPLE = (75, 0, 75)  # 진한 보라색

# 파이게임 화면 생성
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Object Viewer")
clock = pygame.time.Clock()

# 3D 객체 데이터 정의 (정육면체, 정이십면체, 정사면체)
objects = {
    "cube": {
        "vertices": [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),  # 뒷면
                     (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)],     # 앞면
        "faces": [
            (0, 1, 2, 3),  # 뒷면
            (4, 5, 6, 7),  # 앞면
            (0, 1, 5, 4),  # 아래
            (2, 3, 7, 6),  # 위
            (0, 3, 7, 4),  # 왼쪽
            (1, 2, 6, 5)   # 오른쪽
        ]
    },
    "icosahedron": {
        "vertices": [
            (0, 1, 1.618), (0, -1, 1.618), (0, 1, -1.618), (0, -1, -1.618),
            (1.618, 0, 1), (-1.618, 0, 1), (1.618, 0, -1), (-1.618, 0, -1),
            (1, 1.618, 0), (-1, 1.618, 0), (1, -1.618, 0), (-1, -1.618, 0)
        ],
        "faces": [
            (0, 1, 4), (0, 4, 8), (0, 8, 9), (0, 9, 5), (0, 5, 1),
            (3, 2, 6), (3, 6, 10), (3, 10, 11), (3, 11, 7), (3, 7, 2),
            (1, 5, 11), (1, 11, 10), (1, 10, 4), (5, 9, 7), (5, 7, 11),
            (9, 8, 2), (9, 2, 7), (8, 4, 6), (8, 6, 2), (4, 10, 6)
        ]
    },
    "tetrahedron": {
        "vertices": [(1, 1, 1), (-1, -1, 1), (-1, 1, -1), (1, -1, -1)],
        "faces": [
            (0, 1, 2),
            (0, 1, 3),
            (0, 2, 3),
            (1, 2, 3)
        ]
    }
}

# 3D 좌표를 2D로 투영하는 함수
def project(point, angle_x, angle_y, distance):
    x, y, z = point
    cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
    cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)

    xz = cos_y * x - sin_y * z
    z = sin_y * x + cos_y * z
    x = xz

    yz = cos_x * y - sin_x * z
    z = sin_x * y + cos_x * z
    y = yz

    factor = distance / (z + 5)
    x2d = int(WIDTH // 2 + x * factor * 100)
    y2d = int(HEIGHT // 2 - y * factor * 100)

    return (x2d, y2d), z

# 카메라와 면의 거리를 계산하는 함수
def calculate_distance_to_camera(face, vertices, angle_x, angle_y):
    x = sum(vertices[i][0] for i in face) / len(face)
    y = sum(vertices[i][1] for i in face) / len(face)
    z = sum(vertices[i][2] for i in face) / len(face)
    
    cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
    cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)

    xz = cos_y * x - sin_y * z
    z = sin_y * x + cos_y * z
    x = xz

    yz = cos_x * y - sin_x * z
    z = sin_x * y + cos_x * z
    y = yz

    distance = math.sqrt(x**2 + y**2 + (z + 1)**2)
    return distance

# 프로그램 상태
state = "menu"
current_object = None
angle_x, angle_y = 0, 0  # 회전 각도
distance = 2  # 카메라 거리
wireframe = False

# 화면 그리기
def draw_object():
    global angle_x, angle_y, wireframe

    vertices = current_object["vertices"]
    faces = current_object["faces"]
    projected_points = []
    
    # 정점 투영
    for point in vertices:
        projected, z = project(point, angle_x, angle_y, distance)
        projected_points.append((projected, z))

    # 면 그리기 (와이어프레임 여부에 따라 다르게 처리)
    faces_sorted = sorted(faces, key=lambda face: sum(projected_points[i][1] for i in face), reverse=True)
    for face in faces_sorted:
        points = [projected_points[i][0] for i in face]
        vertices_in_face = [vertices[i] for i in face]

        # 카메라와 면의 거리 계산
        distance_to_camera = calculate_distance_to_camera(face, vertices, angle_x, angle_y)

        # 거리 값에 따라 밝기 계산 (거리가 가까울수록 밝고, 멀수록 어두운 색)
        brightness = 1 / (distance_to_camera + 0.1)  # 가까울수록 밝게 (distance_to_camera + 0.1은 너무 밝게 나오는 것 방지)

        # 그라데이션의 강도를 조정
        brightness = min(brightness, 2.5)  # 최대 밝기 정도를 더 강하게 조정
        
        # 면 채우기
        if not wireframe:
            color = tuple(max(0, min(int(c * brightness), 200)) for c in PURPLE)
            pygame.draw.polygon(screen, color, points)

        # 선 색을 진한 보라색으로 변경
        edge_color = PURPLE if not wireframe else WHITE
        pygame.draw.polygon(screen, edge_color, points, 2)

# 버튼 클래스
class Button:
    def __init__(self, text, x, y, w, h, callback):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.callback = callback

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        font = pygame.font.SysFont(None, 36)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def click(self, pos):
        if self.rect.collidepoint(pos):
            self.callback()

# 버튼 설정
buttons = [
    Button("Cube", 100, 200, 200, 50, lambda: set_object("cube")),
    Button("Icosahedron", 100, 300, 200, 50, lambda: set_object("icosahedron")),
    Button("Tetrahedron", 100, 400, 200, 50, lambda: set_object("tetrahedron")),
]

# 객체 설정 함수
def set_object(name):
    global state, current_object
    state = "view"
    current_object = objects[name]

# 메인 루프
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if state == "view":
                if event.key == pygame.K_SPACE:
                    wireframe = not wireframe
                elif event.key == pygame.K_ESCAPE:
                    state = "menu"
            elif state == "menu" and event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and state == "menu":
            for button in buttons:
                button.click(event.pos)
        elif event.type == pygame.MOUSEWHEEL and state == "view":
            if event.y > 0:  # 휠 위로 스크롤
                distance = max(0.5, distance - 0.1)  # 확대 (최소값 0.5)
            elif event.y < 0:  # 휠 아래로 스크롤
                distance = min(5, distance + 0.1)  # 축소 (최대값 5)

    if state == "menu":
        for button in buttons:
            button.draw(screen)
    elif state == "view":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            angle_y -= 0.05
        if keys[pygame.K_RIGHT]:
            angle_y += 0.05
        if keys[pygame.K_UP]:
            angle_x += 0.05
        if keys[pygame.K_DOWN]:
            angle_x -= 0.05

        draw_object()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()