"""
client.py

The client side program, displays current ball positions

Authors:
MOD0912
Nilusink
MelonenBuby
"""

from core.client import Client, Thread
from traceback import format_exc
from core.classes import Vec2
from time import sleep
import typing as tp
import math as m
import pygame
import json


# Connection settings
SERVER_IP: str = "192.168.0.138"
SERVER_PORT: int = 8888


pygame.init()
pygame.font.init()
FONT = pygame.font.SysFont(None, 24)
HEADING = pygame.font.SysFont(None, 60)

PERM_SHOW: list[tuple[tp.Callable, list, dict]] = []


class _Balls(pygame.sprite.Group):
    ...


# create ONLY instance
Balls = _Balls()


class Ball(pygame.sprite.Sprite):
    is_player: bool = False
    velocity: Vec2 = ...
    tries: int = 0

    def __init__(self, pos: tuple[float, float]) -> None:
        super().__init__(Balls)
        self.color = (255, 0, 0, 255)
        self.player_color = (0, 255, 0, 255)
        self.pos_x_y = pos
        self.circle_radius = 12
        self.border_width = 0  # 0 = filled circle

        # self.image =
        self.image = pygame.surface.Surface((self.circle_radius * 2,) * 2, pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, self.color, (self.circle_radius,) * 2, self.circle_radius)

        self.update_rect()

    @property
    def screen_position(self) -> tuple[float, float]:
        screen_info = pygame.display.Info()
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
        self.image.fill((0, 0, 0, 0))
        if self.is_player:
            pygame.draw.circle(self.image, self.player_color, (self.circle_radius,) * 2, self.circle_radius)

        else:
            pygame.draw.circle(self.image, self.color, (self.circle_radius,) * 2, self.circle_radius)

        # draw tries
        tries_text = FONT.render(str(self.tries), True, (0, 0, 0, 255))
        self.image.blit(tries_text, (6, 6))

        self.update_rect()


with open('Maps/Map1.json') as f:
    data = json.load(f)

# create client
client = Client(server_ip=SERVER_IP, port=SERVER_PORT, debug_mode=True)


def main() -> None:
    white = (255, 255, 255)
    screen_info = pygame.display.Info()
    original_window_size = (screen_info.current_w, screen_info.current_h)
    screen = pygame.display.set_mode(original_window_size, pygame.FULLSCREEN)
    pygame.display.set_caption("Mini-Golf")
    active = True
    clock = pygame.time.Clock()

    # create ball surface
    top_layer = pygame.Surface(original_window_size, pygame.SRCALPHA, 32)

    def update_handler() -> None:
        """
        handle server updates
        """
        nonlocal player

        while active:
            try:
                ball_pos = client.received_msg
                if ball_pos is None:
                    sleep(0.01)
                    continue

                while len(Balls.sprites()) < len(ball_pos["balls"]):
                    Ball((0, 0))

                for j, ball in enumerate(ball_pos["balls"]):
                    PERM_SHOW.clear()

                    current_ball: Ball | pygame.sprite.Sprite = Balls.sprites()[j]
                    if client.ID == ball["id"]:  # check if the currently updated ball is the player
                        current_ball.is_player = True
                        player = current_ball

                        if ball["on_target"]:
                            fg = (255, 255, 125, 255)
                            bg = (0, 0, 0, 125)
                            text = HEADING.render("You won!", False, fg, bg)
                            PERM_SHOW.append((
                                top_layer.blit,
                                [text, [100, 100]],
                                {},
                            ))
                            text = HEADING.render(f"Tries: {ball['tries']}", False, fg, bg)
                            PERM_SHOW.append((
                                top_layer.blit,
                                [text, [100, 150]],
                                {},
                            ))

                    else:
                        current_ball.is_player = False

                    x = ball["x"]
                    y = ball["y"]

                    current_ball.update_pos(x, y)
                    current_ball.velocity = Vec2.from_cartesian(*ball["vel"])
                    current_ball.tries = ball["tries"]

            except (Exception,):
                print(f"exception in thread update-handle:\n{format_exc()}\n")

    Thread(target=update_handler).start()

    player: Ball = ...
    while active:
        window_size = (screen_info.current_w, screen_info.current_h)
        w_w = window_size[0]
        w_h = window_size[1]

        mouse_up = False
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    active = False

                case pygame.MOUSEBUTTONUP:
                    mouse_up = True

                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            active = False
                        case pygame.K_RETURN:
                            print("respawning")
                            client.respawn()

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
                pos = Vec2.from_cartesian(*pos)
                delta = mouse_pos - pos

                off = delta.copy()
                orig_delta = delta.copy()
                delta.length -= min_rad

                delta.x /= max_rad - min_rad
                delta.y /= max_rad - min_rad

                if min_rad < orig_delta.length < max_rad:
                    # green: minimum
                    # orange-ish: center
                    # red: maximum
                    val = m.sin((m.pi / 2) * delta.length)
                    r_val = 255 * val
                    g_val = 255 * m.sin((m.pi / 2) * (1 - delta.length))
                    a_val = 60 + 10 * abs(m.sin((m.pi / 2) * (delta.length - .5)))

                    pygame.draw.circle(top_layer, (r_val, g_val, 0, a_val), pos.xy, max_rad)  # lighter circle (aiming)

                else:
                    pygame.draw.circle(top_layer, (255, 0, 0, 40), pos.xy, max_rad)     # lighter circle (default)

                pygame.draw.circle(top_layer, (0, 0, 0, 255), pos.xy, min_rad)         # transparent circle
                pygame.draw.circle(top_layer, (255, 0, 0, 255), pos.xy, max_rad, 1)    # outer circle
                pygame.draw.circle(top_layer, (255, 0, 0, 255), pos.xy, min_rad, 1)    # inner circle

                if min_rad < orig_delta.length < max_rad:
                    off.length = min_rad
                    p0 = pos + off
                    off.length = max_rad
                    p1 = pos + off

                    pygame.draw.line(top_layer, (255, 255, 255, 255), p0.xy, p1.xy, 1)
                    pygame.draw.circle(top_layer, (255, 255, 255, 125), pos.xy, orig_delta.length, 1)  # mouse circle
                    pygame.draw.circle(top_layer, (255, 255, 255, 255), mouse_pos.xy, 5)    # mouse indicator

                    perc = round(delta.length * 100)

                    text_pos = mouse_pos + Vec2.from_cartesian(-40, -20)

                    text = FONT.render(f"{perc}%", True, (255, 255, 255, 255))
                    top_layer.blit(text, text_pos.xy)

                    if mouse_up:    # shot
                        client.shoot({
                            "vector": [delta.x, delta.y]
                        })

        Balls.update()
        Balls.draw(top_layer)

        # draw PERM_SHOW
        for func, args, kwargs in PERM_SHOW:
            print(f"drawing {func.__name__}(*{args}, **{kwargs})")
            func(*args, **kwargs)

        screen.blit(top_layer, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    client.end()
    pygame.quit()
    quit()


if __name__ == '__main__':
    main()
