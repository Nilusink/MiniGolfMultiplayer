"""
server.py

Runs the program, simulates collision and targets

Author:
Nilusink
"""
from core.server import Server, Thread, UserRem, UserAdd, UserShoot, UserRespawn
from core.basegame import BaseGame
from core.objects import *
import time
import json


running: bool = True


def main() -> None:
    global running

    # load map
    with open("./Maps/Map1.json", "r") as inp:
        config = json.load(inp)

    num_points = config["total"]

    # draw target
    pos = config["target"]
    Target(Vec2.from_cartesian(pos[0] * 2, pos[1]))

    # draw walls
    for i in range(1, num_points + 1):
        points = config[str(i)]
        p0 = Vec2.from_cartesian(points["p1_x"] * 2, points["p1_y"])
        p1 = Vec2.from_cartesian(points["p2_x"] * 2, points["p2_y"])

        Wall(p0, p1, 1)

    # Create Server
    server = Server(debug_mode=True, game_map=config)
    print("started server, running pygame")

    def server_handler() -> None:
        """
        ment to be executed as thread
        """
        while running:
            events = server.events

            for event in events:
                match event:
                    case UserAdd(user_id=_, time=_):
                        event: UserAdd
                        Ball(Vec2.from_cartesian(*config["spawn_pos"]), user_id=event.user_id)

                    case UserRem(user_id=_, time=_):
                        event: UserRem
                        Balls.rem_user(event.user_id)

                    case UserShoot(user_id=_, time=_):
                        event: UserShoot
                        user = Balls.get_user(event.user_id)
                        direction = Vec2.from_cartesian(*event.msg["vector"])

                        direction.length *= MAX_SPEED

                        user.hit(direction)

                    case UserRespawn(user_id=_, time=_):
                        print("got respawn")
                        event: UserRespawn

                        user = Balls.get_user(event.user_id)
                        user.reset()

                    case _:
                        raise NotImplementedError(f"unknown event type {type(event)}")

    def send_updates() -> None:
        """
        send updated ball positions to clients
        """
        while running:
            out: dict[str, list] = {"balls": []}
            for ball in Balls.sprites().copy():
                ball: Ball

                out["balls"].append({
                    "id": ball.id,
                    "x": ball.position.x / 2,
                    "y": ball.position.y,
                    "vel": ball.velocity.xy,
                    "tries": ball.tries,
                    "on_target": ball.on_target,
                })

            server.send_all(out)

    def calculator() -> None:
        """
        calculate the ball positions
        """
        last_time = time.perf_counter()
        while running:
            this_time = time.perf_counter()
            time_delta = this_time - last_time
            last_time = this_time

            Balls.update(time_delta)

    Thread(target=server_handler).start()
    Thread(target=send_updates).start()
    Thread(target=calculator).start()

    # pygame loop
    while running:
        # clear layers
        BaseGame.screen.fill((0, 0, 0, 0))
        BaseGame.lowest_layer.fill((0, 0, 0, 0))
        BaseGame.wall_layer.fill((0, 0, 0, 0))
        BaseGame.middle_layer.fill((0, 0, 0, 0))
        BaseGame.top_layer.fill((0, 0, 0, 0))

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

    running = False


if __name__ == "__main__":
    main()
    running = False
