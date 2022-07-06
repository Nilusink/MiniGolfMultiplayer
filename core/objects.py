"""
core/objects.py

classes for all walls and balls (sprites) and groups

Author:
Nilusink
"""
import random

from .basegame import BaseGame
from .classes import Vec2
import pygame as pg
import typing as tp
import numpy as np
import cmath as cm


def _is_valid(x: float, y: float) -> bool:
    """
    check if x is between 0..2 and y between 0..1
    """
    if not 0 <= x <= 2 or not 0 <= y <= 1:
        return False

    return True


def _to_screen_size(x: float, y: float) -> tuple[float, float]:
    """
    convert from "percent" scheme to actual screen pixels
    """
    # if not _is_valid(x, y):
    #     raise ValueError("x must be between 0..2. y must be between 0..1")

    x = (x/2) * BaseGame.window_size[0]
    y *= BaseGame.window_size[1]

    return x, y


# groups
class _Walls(pg.sprite.Group):
    def collide(self, ball: "Ball") -> tp.Union[tuple["Wall", tuple[int, int]], None]:
        """
        check if a sprite collides with a wall
        """
        for wall in self.sprites():
            wall: Wall

            # check if they collide (box)
            if pg.sprite.collide_rect(wall, ball):
                # check if they collide (by pixel)
                pos = pg.sprite.collide_mask(ball, wall)
                if pos:
                    return wall, pos

        return


class _Balls(pg.sprite.Group):
    def get_user(self, user_id: str) -> "Ball":
        for user in self.sprites():
            user: Balls

            if user.id == user_id:
                return user

    def rem_user(self, user_id: str) -> None:
        user = self.get_user(user_id=user_id)
        self.remove(user)


class _Targets(pg.sprite.Group):
    def collide(self, ball: "Ball") -> tp.Union["Target", None]:
        """
        check if a sprite collides with a wall
        """
        for target in self.sprites():
            target: Target

            if pg.sprite.collide_mask(ball, target):
                return target

        return


# actual groups
Walls = _Walls()
Balls = _Balls()
Targets = _Targets()


# sprites
class Wall(pg.sprite.Sprite):
    extra_size: int = 10
    ellipse_rect: pg.Rect

    def __init__(self, p0, p1, thickness: int = 1) -> None:
        self.x = min([p0.x, p1.x])
        self.y = min([p0.y, p1.y])

        x1 = max([p0.x, p1.x])
        y1 = max([p0.y, p1.y])

        self.width = x1 - self.x
        self.height = y1 - self.y

        self._collision_vector = (p0 - p1).normalize()

        super().__init__(Walls)

        self.update_rect()

        width, height = _to_screen_size(self.width, self.height)

        width += 2 * self.extra_size
        height += 2 * self.extra_size

        self.image = pg.surface.Surface(
            (width, height),
            pg.SRCALPHA, 32
        )

        x0 = (p0.x - self.x)
        y0 = (p0.y - self.y)

        x1 = (p1.x - self.x)
        y1 = (p1.y - self.y)

        (x0, y0) = _to_screen_size(x0, y0)
        (x1, y1) = _to_screen_size(x1, y1)

        x0 += self.extra_size
        y0 += self.extra_size
        x1 += self.extra_size
        y1 += self.extra_size

        pg.draw.line(self.image, (255, 0, 0, 255), (x0, y0), (x1, y1), width=thickness)

        _pos, (width, height) = self.get_pygame_values()
        width += 2 * self.extra_size - 2
        height += 2 * self.extra_size - 2
        pg.draw.rect(self.image, (125, 0, 0, 125), pg.Rect(1, 1, width, height), width=1)

    def get_pygame_values(self) -> tuple[list[float, float], list[float, float]]:
        return list(_to_screen_size(self.x, self.y)), list(_to_screen_size(self.width, self.height))

    def get_collision_vector(self, _collision_point: Vec2) -> Vec2:
        return self._collision_vector.copy()

    def update_rect(self) -> None:
        (x, y), (width, height) = self.get_pygame_values()
        x -= self.extra_size
        y -= self.extra_size

        width += 2 * self.extra_size
        height += 2 * self.extra_size

        self.rect = pg.Rect(x, y, width, height)


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
            _to_screen_size(self.width, self.height),
            pg.SRCALPHA, 32
        )

        pg.draw.ellipse(self.image, (255, 0, 0, 255), self.ellipse_rect, width=thickness)

    def get_pygame_values(self) -> tuple[list[float, float], list[float, float]]:
        return list(_to_screen_size(self.x, self.y)), list(_to_screen_size(self.width, self.height))

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
    size: float = .025
    _velocity: Vec2
    _tries: int = 0
    position: Vec2
    id: str

    def __init__(self, origin: Vec2, user_id: str = ...) -> None:
        if user_id is ...:
            user_id = str(random.randint(0, 1_000_000))

        self.id = user_id

        self.position = origin.copy()
        self._origin = origin.copy()
        self._velocity = Vec2()

        super().__init__(Balls)

        self.image = pg.surface.Surface([self.screen_size] * 2, pg.SRCALPHA, 32)
        pg.draw.circle(self.image, (255, 0, 0, 255), [self.screen_size / 2] * 2, radius=self.screen_size / 2)

        identifier = user_id[-1]

        text = BaseGame.font.render(identifier, False, (0, 0, 0, 255))

        self.image.blit(text, (6, 5))

        self.update_rect()

    @property
    def screen_size(self) -> float:
        s = _to_screen_size(self.size, 0)[0]
        return s

    @property
    def screen_position(self) -> tuple[float, float]:
        return _to_screen_size(self.position.x, self.position.y)

    @property
    def tries(self) -> int:
        """
        how often the ball was hit to this point
        """
        return self._tries

    @property
    def velocity(self) -> Vec2:
        return self._velocity

    def update_rect(self) -> None:
        x = (self.position.x - self.size / 2)
        y = (self.position.y - self.size / 2)

        self.rect = pg.Rect(
            *_to_screen_size(x, y),
            *[self.screen_size] * 2,
        )

    def update(self, delta: float) -> None:
        if self._velocity.length == 0:
            return

        self.position += self._velocity * delta

        if self._velocity.length > .0005:
            self._velocity.length *= .99

        else:
            self._velocity.length = 0

        # check for collision
        res = Walls.collide(self)

        if res is not None:
            wall, pos = res
            self.position -= self._velocity * delta
            self._velocity.reflect(wall.get_collision_vector(Vec2.from_cartesian(*pos)))
            self.position += self._velocity * delta

        # check for hitting the target
        target = Targets.collide(self)

        if target is not None and self._velocity.length < 0.001:
            self._velocity = Vec2()

        # check if the ball is out of screen
        if not _is_valid(*self.position.xy):
            self.reset()

        self.update_rect()

    def hit(self, speed: Vec2) -> None:
        """
        "hit" a ball with a cup.
        A ball can only be hit if it stands still (velocity = 0)
        """
        if not self._velocity.length == 0:
            return

        self._tries += 1
        self._velocity = speed.copy()

    def reset(self) -> None:
        """
        but a ball back to its original position (without any velocity
        """
        self.position = self._origin.copy()
        self._velocity = Vec2()


class Target(pg.sprite.Sprite):
    size: float = .01
    position: Vec2

    def __init__(self, position: Vec2) -> None:
        self.position = position

        super().__init__(Targets)

        self.image = pg.surface.Surface(
            (self.screen_size,) * 2,
            pg.SRCALPHA, 32,
        )

        self.update_rect()

        pg.draw.circle(self.image, (255, 255, 0, 255), (self.screen_size / 2,) * 2, self.screen_size / 2)

    @property
    def screen_size(self) -> float:
        s = _to_screen_size(self.size, 0)[0]
        return s

    @property
    def screen_position(self) -> tuple[float, float]:
        return _to_screen_size(self.position.x, self.position.y)

    def update_rect(self) -> None:
        x, y = self.screen_position

        x -= self.screen_size / 2
        y -= self.screen_size / 2

        self.rect = pg.Rect(x, y, *(self.screen_size,) * 2)
