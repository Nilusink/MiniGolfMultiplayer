"""
core/server.py

Server-class for cummunication with events on serverside

Authors: MelonenBuby, Nilusink
Date:   29.06.2022
"""

################################################################################
#                                Import Modules                                #
################################################################################

from dataclasses import dataclass
from json import dumps, loads
from threading import Thread
from typing import Union
from time import time, sleep
import socket


################################################################################
#                           Constants / Settings                              #
################################################################################

ENCRYPTION: str = "UTF-32"
PORT: int = 8888


################################################################################
#                                 Exceptions                                   #
################################################################################

class MultipleDataReceived(Exception):
    ...


################################################################################
#                                   Events                                     #
################################################################################

@dataclass(frozen=True)
class UserAdd:
    """
    Event for new users
    """
    user_id: str
    time: float


@dataclass(frozen=True)
class UserRem: # noqa
    """
    Event for removed/disconnected users
    """
    user_id: str
    time: float


@dataclass(frozen=True)
class UserShoot: # noqa
    """
    Event for user data / shoots
    """
    user_id: str
    time: float
    msg: dict


################################################################################
#                                   Server                                     #
################################################################################

class Server(socket.socket):
    __clients: dict[str, socket.socket]
    __events: list[Union[UserAdd, UserRem, UserShoot]]
    __id_counter: int
    debug_mode: bool
    running: bool

    def __init__(self, debug_mode: bool | None = False) -> None:
        """
        Server for communicating between game calculating and game GUI
        """

        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.debug_mode = debug_mode

        self._print(f"<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>")
        self._print()
        self._print(f"SERVER STARTED:")
        self._print(f" - IP:     {socket.gethostbyname(socket.gethostname())}")
        self._print(f" - PORT:   {PORT}")
        self._print()
        self._print(f"<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>")

        self.bind(("0.0.0.0", PORT))
        self.listen()

        self.running = True
        self.__clients = {}
        self.__events = []
        self.__id_counter = 0

        Thread(target=self.__new_clients, args=()).start()

    def _print(self, *msg: any) -> None:
        """
        Only print if debug mode is on

        :param msg: Messages to print
        """

        if self.debug_mode:
            print("SERVER:", *msg)

    @property
    def events(self) -> list[UserAdd, UserRem, UserShoot]:
        """
        Returns events since the last event query
        ATTENTION: This deletes the caching of the events

        :return List of all different events
        """

        events = self.__events
        self.__events = []
        return events

    def send_user(self, user_id: str, msg: dict) -> None:
        """
        Sends messages to a single clients/users

        :param user_id: ID of the user/client to send to
        :param msg: Message to send to all users/clients
        """

        msg_str = dumps(msg)
        msg_byte = msg_str.encode(ENCRYPTION)
        self.__clients[user_id].send(msg_byte)

    def send_all(self, msg: dict) -> None:
        """
        Sends messages to all clients/users

        :param msg: Message to send to all users/clients
        """

        for client in self.__clients.copy():
            try:
                msg_str = dumps(msg)
                msg_byte = msg_str.encode(ENCRYPTION)
                self.__clients[client].send(msg_byte)

            except OSError:
                continue

    def __client_receive_handler(self, user_id: str, client: socket.socket) -> None:
        """
        Receives messages from the clients and saves it as events

        :param user_id: ID of the user/client
        :param client: Socket of the user/client
        """
        client.settimeout(.1)
        connected = True

        while connected:
            try:
                msg = client.recv(1024)

                if msg == b"":
                    client.close()
                    raise ConnectionResetError  # to disconnect the user (event)

                msg_str = msg.decode(ENCRYPTION)
                msg_dic = loads(msg_str)

                event = UserShoot(user_id=user_id, time=time(), msg=msg_dic)
                for single_event in self.__events:
                    if type(single_event) == UserShoot and single_event.user_id == user_id:
                        raise MultipleDataReceived("Client already sent data")
                self.__events.append(event)
                self._print(f"{user_id} SENT: {msg_dic}")

            except ConnectionResetError:
                self._print(f"USER DISCONNECTED: {user_id}")
                self.__events.append(UserRem(user_id=user_id, time=time()))
                connected = False

            except TimeoutError:
                continue

            except OSError:
                return

    def __new_clients(self) -> None:
        """
        Looks for new clients and assigns them a new thread
        """

        while self.running:
            cl, add = self.accept()

            user_id = "user_{:03d}".format(self.__id_counter)
            self._print("NEW CLIENT: ", user_id, cl, add)

            cl.send(user_id.encode(ENCRYPTION))

            self.__events.append(UserAdd(user_id=user_id, time=time()))
            self.__clients[user_id] = cl
            Thread(target=self.__client_receive_handler, args=(user_id, cl,)).start()

            self.__id_counter += 1

    def end(self) -> None:
        self.running = False


if __name__ == "__main__":
    Server(debug_mode=True)


