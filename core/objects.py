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

            if x0 < ball.position.x < x1 and y0 < ball.position.y < y1:
                if pg.sprite.collide_mask(ball, wall):
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

    def __init__(self, p0: Vec2, p1: Vec2, thickness: float) -> None:
        self.thickness = thickness
        self.p0 = p0
        self.p1 = p1

        super().__init__(Walls)

        pos, size = self.get_pygame_values()

        self.image = pg.surface.Surface(size, pg.SRCALPHA, 32)

        x0 = p0.x - pos[0]
        y0 = p0.y - pos[1]

        x1 = p1.x - pos[0]
        y1 = p1.y - pos[1]

        pg.draw.line(self.image, (255, 0, 0, 255), (x0, y0), (x1, y1))
        print(f"drawing line between {x0, y0}, {x1, y1}")

        self.update_rect()

    def get_pygame_values(self) -> tuple[list[int, int], list[int, int]]:
        x0 = min(self.p0.x, self.p1.x)
        y0 = min(self.p0.y, self.p1.y)

        x1 = max(self.p0.x, self.p1.x)
        y1 = max(self.p0.y, self.p1.y)

        return [x0, y0], [x1-x0, y1-y0]

    def update_rect(self) -> None:
        pos, size = self.get_pygame_values()

        # make sure the rect is at least 1 pixel tall / wide
        size[0] = size[0] if size[0] >= 0 else 1
        size[1] = size[1] if size[1] >= 0 else 1

        self.rect = pg.Rect(*pos, *size)


class Ball(pg.sprite.Sprite):
    loss_per_sec: float = .05
    size: float = 20
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

        self.image = pg.surface.Surface([self.size] * 2, pg.SRCALPHA, 32)
        pg.draw.circle(self.image, (255, 0, 0, 255), [self.size / 2] * 2, radius=self.size / 2)

        self.update_rect()

    def update_rect(self) -> None:
        self.rect = pg.Rect(
            self.position.x - self.size / 2,
            self.position.y - self.size / 2,
            self.size,
            self.size
        )

    def update(self, delta: float) -> None:
        self.position += self.velocity * delta

        if self.velocity.length > 0:
            self.velocity.length -= self.loss_per_sec

        if self.velocity.length < 0:
            self.velocity.length = 0

        # check for collision
        wall = Walls.collide(self)

        if wall is not None:
            collided_with: list[wall] = [wall]
            wall_angle = wall.p1 - wall.p0
            self.velocity.reflect(wall_angle)

            no_coll = 0
            while no_coll < 1:
                self.position += self.velocity * delta * 2

                wall = Walls.collide(self)
                if wall is None or wall in collided_with:
                    no_coll += 1
                    continue

                collided_with.append(wall)
                wall_angle = wall.p1 - wall.p0
                self.velocity.reflect(wall_angle)

        self.update_rect()
