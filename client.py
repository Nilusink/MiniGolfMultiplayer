"""
client.py

The client side program, displays current ball positions

Authors:
MOD0912
Nilusink
"""
from core.client import Client, Thread
from time import sleep
import pygame, json

pygame.init()
black = (0, 0, 0)
white = (255, 255, 255)
screen_info = pygame.display.Info()
original_window_size = (screen_info.current_w, screen_info.current_h)
w_w = original_window_size[0]
w_h = original_window_size[1]
screen = pygame.display.set_mode(original_window_size, pygame.RESIZABLE)
pygame.display.set_caption("Minigolf")
aktiv = True
clock = pygame.time.Clock()


class _Balls(pygame.sprite.Group):
    ...


Balls = _Balls()


class Ball(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[float, float]) -> None:
        super().__init__(Balls)
        self.colour = (0, 255, 0, 255)  # green
        self.pos_x_y = pos
        self.circle_radius = 12
        self.border_width = 0  # 0 = filled circle

        # self.image =
        self.image = pygame.surface.Surface((self.circle_radius * 2,) * 2, pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, self.colour, (self.circle_radius,) * 2, self.circle_radius)

        self.update_rect()

    def update_pos(self, x: float, y: float) -> None:
        self.pos_x_y = x, y
        self.update_rect()

    def update_rect(self) -> None:
        window_size = (screen_info.current_w, screen_info.current_h)
        x, y = self.pos_x_y

        x *= window_size[0]
        y *= window_size[1]

        self.rect = pygame.Rect(x, y, *(self.circle_radius * 2,) * 2)

    def update(self) -> None:
        self.update_rect()


with open('Maps/Map1.json') as f:
    data = json.load(f)

# create client
client = Client(server_ip="127.0.0.1", port=8888, debug_mode=True)


def update_handler() -> None:
    """
    handle server updates
    """
    client.send_data({
        "vector": [0, -.016]
    })

    while True:
        ball_pos = client.received_msg
        if ball_pos is None:
            continue

        while len(Balls.sprites()) < len(ball_pos["balls"]):
            Ball((0, 0))

        for i, ball in enumerate(ball_pos["balls"]):
            current_ball: Ball = Balls.sprites()[i]
            x = ball["x"]
            y = ball["y"]

            current_ball.update_pos(x, y)


Thread(target=update_handler).start()

# create ball surface
top_layer = pygame.Surface(original_window_size, pygame.SRCALPHA, 32)

while aktiv:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            aktiv = False

    # reset layers
    screen.fill((0, 0, 0, 0))
    top_layer.fill((0, 0, 0, 0))

    total = data["total"]
    for i in range(1, total + 1):
        i = str(i)
        p1_x = data[i]["p1_x"]
        p1_y = data[i]["p1_y"]
        p2_x = data[i]["p2_x"]
        p2_y = data[i]["p2_y"]
        # print(p1_y*w_h)
        # print(p2_x*w_w)
        pygame.draw.line(screen, white, (p1_x * w_w, p1_y * w_h), (p2_x * w_w, p2_y * w_h))

    Balls.update()
    Balls.draw(top_layer)

    screen.blit(top_layer, (0, 0))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
quit()
# "": {"p1_x": 0., "p1_y": 0., "p2_x": 0., "p2_y": 0.}
