import pygame as pg


class _BaseGame:
    def __init__(self, window_size: tuple[int, int] = ...) -> None:
        # initialize pygame
        pg.init()
        pg.font.init()

        self.to_draw = []

        if window_size is ...:
            screen_info = pg.display.Info()
            window_size = (screen_info.current_w, screen_info.current_h)

        self.window_size = window_size

        # create window
        self.times = []
        self.times_values = []
        self.times_Values2 = []
        self.screen = pg.display.set_mode(window_size, pg.RESIZABLE)
        self.lowest_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.wall_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.middle_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.top_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.font = pg.font.SysFont(None, 24)
        pg.display.set_caption("MiniGolf")


# initialize game
BaseGame = _BaseGame((1500, 750))
