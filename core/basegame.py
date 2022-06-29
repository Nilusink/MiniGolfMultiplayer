import pygame as pg
import typing as tp


class _BaseGame:
    def __init__(self, window_size: tuple[int, int] = ...) -> None:
        # initialize pygame
        pg.init()
        pg.font.init()

        if window_size is ...:
            screen_info = pg.display.Info()
            window_size = (screen_info.current_w, screen_info.current_h)

        # create window
        self.times = []
        self.times_values = []
        self.times_Values2 = []
        self.screen = pg.display.set_mode(window_size, pg.SCALED)
        self.lowest_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.wall_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.middle_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.top_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.font = pg.font.SysFont(None, 24)
        pg.display.set_caption("MiniGOlf")


# initialize game
BaseGame = _BaseGame()
