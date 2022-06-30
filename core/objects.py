"""
classes for all walls and balls (sprites) and groups

Author:
Nilusink
"""
import random

from .basegame import BaseGame
from .classes import Vec2
from random import randint
import pygame as pg
import typing as tp
import numpy as np
import cmath as cm


# groups
class _Walls(pg.sprite.Group):
    def collide(self, ball: "Ball") -> tp.Union["Wall", None]:
        """
        check if a sprite collides with a wall
        """
        for wall in self.sprites():
            wall: Wall
            (x0, y0), (width, height) = wall.get_pygame_values()

            x1 = x0 + width
            y1 = y0 + width

            # if x0 < ball.position.x < x1 and y0 < ball.position.y < y1:
            #     print("in box")
            if pg.sprite.collide_mask(ball, wall):
                print("collision")
                return wall

        return


class _Balls(pg.sprite.Group):
    def get_user(self, user_id: str) -> None:
        for user in self.sprites():
            user: Balls

            if user.id == user_id:
                return user


# actual groups
Walls = _Walls()
Balls = _Balls()


# sprites
class Wall(pg.sprite.Sprite):
    thickness: float
    p0: Vec2
    p1: Vec2

    def __init__(self, p0: Vec2, p1: Vec2, thickness: int) -> None:
        self.thickness = thickness
        self.p0 = p0
        self.p1 = p1

        super().__init__(Walls)

        pos, size = self.get_pygame_values()

        self.image = pg.surface.Surface(size, pg.SRCALPHA, 32)

        x0 = (p0.x * BaseGame.window_size[0]) - pos[0]
        y0 = (p0.y * BaseGame.window_size[1]) - pos[1]

        x1 = (p1.x * BaseGame.window_size[0]) - pos[0]
        y1 = (p1.y * BaseGame.window_size[1]) - pos[1]

        pg.draw.line(self.image, (255, 0, 0, 255), (x0, y0), (x1, y1), width=thickness)

        self.update_rect()

    def get_pygame_values(self) -> tuple[list[int, int], list[int, int]]:
        x0 = min(self.p0.x, self.p1.x)
        y0 = min(self.p0.y, self.p1.y)

        x1 = max(self.p0.x, self.p1.x)
        y1 = max(self.p0.y, self.p1.y)

        # go from 0..1 to 0..screensize
        x0 *= BaseGame.window_size[0]
        x1 *= BaseGame.window_size[1]

        width = (x1 - x0) * BaseGame.window_size[0]
        height = (y1 - y0) * BaseGame.window_size[1]

        return [x0, y0], [width, height]

    def get_collision_vector(self, _collision_point: Vec2) -> Vec2:
        return (self.p0 - self.p1).normalize()

    def update_rect(self) -> None:
        pos, size = self.get_pygame_values()

        # make sure the rect is at least 1 pixel tall / wide
        size[0] = size[0] if size[0] >= 0 else 1
        size[1] = size[1] if size[1] >= 0 else 1

        self.rect = pg.Rect(*pos, *size)


class EllipseWall(pg.sprite.Sprite):
    ellipse_rect: pg.Rect

    def __init__(self, x: float, y: float, width: float, height: float, thickness: int = 1) -> None:
        self.height = height
        self.width = width
        self.x = x
        self.y = y

        super().__init__(Walls)

        self.update_rect()
        self.image = pg.surface.Surface(
            (width * BaseGame.window_size[0], height * BaseGame.window_size[1]),
            pg.SRCALPHA, 32
        )

        pg.draw.ellipse(self.image, (255, 0, 0, 255), self.ellipse_rect, width=thickness)

    def get_pygame_values(self) -> tuple[list[float, float], list[float, float]]:
        x = self.x * BaseGame.window_size[0]
        y = self.y * BaseGame.window_size[1]
        width = self.width * BaseGame.window_size[0]
        height = self.width * BaseGame.window_size[1]

        return [x, y], [width, height]

    def get_collision_vector(self, collision_point: Vec2) -> Vec2:
        p1, p2 = self.focal_points

        p1 = Vec2.from_cartesian(*p1)
        p2 = Vec2.from_cartesian(*p2)

        to_p1 = collision_point - p1
        to_p2 = collision_point - p2

        coll = Vec2.from_polar(angle=(to_p1.angle + to_p2.angle) / 2, length=500)
        coll.angle += np.pi / 2

        return coll.normalize()

    def update_rect(self) -> None:
        (x, y), (width, height) = self.get_pygame_values()
        self.rect = pg.Rect(x, y, width, height)
        self.ellipse_rect = pg.Rect(0, 0, width, height)

    @property
    def focal_points(self) -> tuple[list[float, float], list[float, float]]:
        """
        calculate the focal points of the ellipsis
        """
        (x0, y0), (width, height) = self.get_pygame_values()

        x_c = x0 + width / 2
        y_c = y0 + height / 2

        a = width / 2
        b = height / 2

        e = cm.sqrt(a**2 - b**2)

        e_x = e.real
        e_y = e.imag

        p1 = [x_c + e_x, y_c + e_y]
        p2 = [x_c - e_x, y_c - e_y]

        return p1, p2


class Ball(pg.sprite.Sprite):
    loss_per_sec: float = .000025
    size: float = .01
    velocity: Vec2
    position: Vec2
    id: str

    def __init__(self, origin: Vec2, velocity: Vec2, user_id: str = ...) -> None:
        if user_id is ...:
            user_id = str(random.randint(0, 1_000_000))

        self.id = user_id

        self.velocity = velocity
        self.position = origin

        super().__init__(Balls)

        self.image = pg.surface.Surface([self.screen_size] * 2, pg.SRCALPHA, 32)
        pg.draw.circle(self.image, (255, 0, 0, 255), [self.screen_size / 2] * 2, radius=self.screen_size / 2)

        self.update_rect()

    @property
    def screen_size(self) -> float:
        s = self.size * BaseGame.window_size[0]
        return s

    @property
    def screen_position(self) -> tuple[float, float]:
        x = self.position.x * BaseGame.window_size[0]
        y = self.position.y * BaseGame.window_size[1]

        return x, y

    def update_rect(self) -> None:
        self.rect = pg.Rect(
            (self.position.x - self.size / 2) * BaseGame.window_size[0],
            (self.position.y - self.size / 2) * BaseGame.window_size[1],
            self.size * BaseGame.window_size[0],
            self.size * BaseGame.window_size[1],
        )

    def update(self, delta: float) -> None:
        self.position += self.velocity * delta

        # if self.velocity.length > 0:
        #     self.velocity.length -= self.loss_per_sec

        if self.velocity.length < 0:
            self.velocity.length = 0

        # check for collision
        wall = Walls.collide(self)

        if wall is not None:
            self.velocity.reflect(wall.get_collision_vector(Vec2.from_cartesian(*self.screen_position)))

            for _ in range(4):
                self.position += self.velocity * delta

        self.update_rect()
