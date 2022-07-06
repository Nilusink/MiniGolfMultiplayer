"""
client.py

The client side program, displays current ball positions

Authors:
MOD0912
Nilusink
"""
from core.client import Client, Thread
from core.classes import Vec2
from traceback import format_exc
import pygame
import json

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
    velocity: Vec2 = ...

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

    @property
    def screen_position(self) -> tuple[float, float]:
        window_size = (screen_info.current_w, screen_info.current_h)
        x, y = self.pos_x_y

        x *= window_size[0]
        y *= window_size[1]

        return x, y

    @property
    def screen_center(self) -> tuple[float, float]:
        x, y = self.screen_position
        x += self.circle_radius
        y += self.circle_radius

        return x, y

    def update_pos(self, x: float, y: float) -> None:
        self.pos_x_y = x, y
        self.update_rect()

    def update_rect(self) -> None:
        x, y = self.screen_position

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
    global player

    while aktiv:
        try:
            ball_pos = client.received_msg
            if ball_pos is None:
                continue

            while len(Balls.sprites()) < len(ball_pos["balls"]):
                Ball((0, 0))

            for i, ball in enumerate(ball_pos["balls"]):
                current_ball: Ball = Balls.sprites()[i]
                if client.ID == ball["id"]:  # check if the currently updated ball is the player
                    player = current_ball

                x = ball["x"]
                y = ball["y"]

                current_ball.update_pos(x, y)
                current_ball.velocity = Vec2.from_cartesian(*ball["vel"])

        except (Exception,):
            print(f"exception in thread update-handle:\n{format_exc()}\n")


Thread(target=update_handler).start()

# create ball surface
top_layer = pygame.Surface(original_window_size, pygame.SRCALPHA, 32)

player: Ball = ...
while aktiv:
    mouse_up = False
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                aktiv = False

            case pygame.MOUSEBUTTONUP:
                mouse_up = True

    mouse_pos = Vec2.from_cartesian(*pygame.mouse.get_pos())

    # reset layers
    screen.fill((0, 0, 0, 0))
    top_layer.fill((0, 0, 0, 0))

    total = data["total"]
    # draw walls and targets
    for i in range(1, total + 1):
        i = str(i)
        p1_x = data[i]["p1_x"]
        p1_y = data[i]["p1_y"]
        p2_x = data[i]["p2_x"]
        p2_y = data[i]["p2_y"]
        # print(p1_y*w_h)
        # print(p2_x*w_w)
        pygame.draw.line(screen, white, (p1_x * w_w, p1_y * w_h), (p2_x * w_w, p2_y * w_h))

    target_pos = data["target"]

    pygame.draw.circle(screen, (255, 255, 0, 255), (target_pos[0] * w_w, target_pos[1] * w_h), 10)

    # draw player "aim"
    if player is not ...:
        if player.velocity.length == 0:  # only draw when standing still
            max_rad = 150
            min_rad = 25
            pos = player.screen_center
            pygame.draw.circle(top_layer, (255, 0, 0, 40), pos, max_rad)        # lighter layer
            pygame.draw.circle(top_layer, (0, 0, 0, 255), pos, min_rad)
            pygame.draw.circle(top_layer, (255, 0, 0, 255), pos, max_rad, 1)    # outer circle
            pygame.draw.circle(top_layer, (255, 0, 0, 255), pos, min_rad, 1)    # inner circle

            pos = Vec2.from_cartesian(*pos)
            delta = mouse_pos - pos

            if min_rad < delta.length < max_rad:
                pygame.draw.circle(top_layer, (255, 255, 255, 125), pos.xy, delta.length, 1)    # mouse indicator circle
                pygame.draw.circle(top_layer, (255, 255, 255, 255), mouse_pos.xy, 5)    # mouse indicator

                if mouse_up:    # shot
                    # min_rad = 0, max_rad = 1
                    delta.length -= min_rad

                    delta.x /= max_rad - min_rad
                    delta.y /= max_rad - min_rad

                    client.send_data({
                        "vector": [delta.x, delta.y]
                    })

    Balls.update()
    Balls.draw(top_layer)

    screen.blit(top_layer, (0, 0))

    pygame.display.flip()
    clock.tick(60)

client.end()
pygame.quit()
quit()
# "": {"p1_x": 0., "p1_y": 0., "p2_x": 0., "p2_y": 0.}
