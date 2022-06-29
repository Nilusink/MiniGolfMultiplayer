from core.basegame import BaseGame
from core.objects import *


running: bool = True


def main() -> None:
    print("main called")
    # create some walls
    Wall(Vec2.from_cartesian(200, 0), Vec2.from_cartesian(600, 200), 1)
    Wall(Vec2.from_cartesian(200, 0), Vec2.from_cartesian(0, 200), 1)
    Wall(Vec2.from_cartesian(600, 200), Vec2.from_cartesian(1800, 100), 1)
    Wall(Vec2.from_cartesian(1800, 100), Vec2.from_cartesian(900, 777), 1)
    Wall(Vec2.from_cartesian(900, 777), Vec2.from_cartesian(100, 900), 1)
    Wall(Vec2.from_cartesian(100, 900), Vec2.from_cartesian(0, 200), 1)

    Ball(Vec2.from_cartesian(100, 600), Vec2.from_cartesian(0, -20))

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

        # draw layers
        BaseGame.screen.blit(BaseGame.lowest_layer, (0, 0))
        BaseGame.screen.blit(BaseGame.wall_layer, (0, 0))
        BaseGame.screen.blit(BaseGame.middle_layer, (0, 0))
        BaseGame.screen.blit(BaseGame.top_layer, (0, 0))

        pg.display.flip()


if __name__ == "__main__":
    main()
    running = False
