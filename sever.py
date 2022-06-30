from core.basegame import BaseGame
from core.objects import *


running: bool = True


def main() -> None:
    # create some walls
    EllipseWall(.1, .1, .8, .8, 1)
    EllipseWall(.2, 0, .7, 1, 1)
    Wall(Vec2.from_cartesian(.3, .8), Vec2.from_cartesian(.8, .3), 1)

    Ball(Vec2.from_cartesian(.5, .5)).hit(Vec2.from_cartesian(.008, .004))

    Target(Vec2.from_cartesian(.65, .3))

    while running:
        # clear layers
        BaseGame.screen.fill((0, 0, 0, 0))
        BaseGame.lowest_layer.fill((0, 0, 0, 0))
        BaseGame.wall_layer.fill((0, 0, 0, 0))
        BaseGame.middle_layer.fill((0, 0, 0, 0))
        BaseGame.top_layer.fill((0, 0, 0, 0))

        # update groups
        Balls.update(1)

        # draw groups
        Walls.draw(BaseGame.wall_layer)
        Balls.draw(BaseGame.middle_layer)
        Targets.draw(BaseGame.lowest_layer)

        # draw to draw
        for function, args in BaseGame.to_draw:
            function(*args)

        # draw layers
        BaseGame.screen.blit(BaseGame.lowest_layer, (0, 0))
        BaseGame.screen.blit(BaseGame.wall_layer, (0, 0))
        BaseGame.screen.blit(BaseGame.middle_layer, (0, 0))
        BaseGame.screen.blit(BaseGame.top_layer, (0, 0))

        pg.display.flip()


if __name__ == "__main__":
    main()
    running = False
