"""
core/client.py

Client-class for cummunication with the server

Author: MelonenBuby
Date:   29.06.2022
"""


################################################################################
#                                Import Modules                                #
################################################################################

from threading import Thread
from time import time
import socket
import json

################################################################################
#                           Constants / Settings                              #
################################################################################

SERVER_IP: str = "127.0.0.1"
ENCRYPTION: str = "UTF-8"
PORT: int = 8888


################################################################################
#                                 Exceptions                                   #
################################################################################

class NotReceivedJet(Exception):
    ...


################################################################################
#                                   Client                                     #
################################################################################

class Client(socket.socket):
    __received_msg: list[dict]
    __ping_trigger: int
    debug_mode: bool
    __running: bool
    __game_map: dict
    __ID: str

    def __init__(self, server_ip: str, port: int, debug_mode: bool | None = False) -> None:
        """
        Client for communicating between game calculating and game GUI
        """

        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.debug_mode = debug_mode

        self._print(f"<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>")
        self._print()
        self._print(f"CLIENT IS CONNECTING TO SERVER:")
        self._print(f" - IP:     {server_ip}")
        self._print(f" - PORT:   {port}")
        self._print()
        self._print(f"<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>")

        self.__received_msg = []
        self.__ping_trigger = 0
        self.__running = True
        self.__game_map = {}
        self.__ID = ""

        self.connect((server_ip, port))
        Thread(target=self.__receive, args=()).start()

    @property
    def game_map(self) -> dict:
        if self.__game_map != {}:
            return self.__game_map.copy()
        raise NotReceivedJet("Server haven't sent a map jet or it's just empty")

    @property
    def ID(self) -> str:
        if self.__ID != "":
            return self.__ID
        raise NotReceivedJet("Server haven't sent a ID or it's just empty")

    @property
    def received_msg(self) -> dict | None:
        """
        Returns the oldest received message and deletes it's caching
        :return: Dictonary of the message or none if there is no new messages
        """
        try:
            rec_data = self.__received_msg[0]
            del self.__received_msg[0]
            return rec_data

        except IndexError:
            return None

    def __receive(self) -> None:
        """
        Receives messages from the server in packages and saves them
        """
        recv: bool = False
        data = bytearray()

        while self.__running:
            try:
                msg_byte = self.recv(1)
                if not recv and msg_byte == b'@':
                    recv = True

                elif recv and msg_byte != b"#":
                    data.extend(msg_byte)

                elif recv:
                    msg_str = data.decode(ENCRYPTION)
                    msg = json.loads(msg_str)
                    recv = False
                    data = bytearray()

                    msg_content = msg["content"]
                    match msg["type"]:
                        case "msg":
                            self.__received_msg.append(msg_content)
                        case "ID":
                            print("GOT ID", msg_content)
                            self.__ID = msg_content
                        case "map":
                            print("GOT MAP", msg_content)
                            self.__game_map = msg_content
                        case "PONG":
                            self.__ping_trigger = 0
                        case "_":
                            raise NotImplementedError("Invalid message received with type={msg['type']}")

            except (ConnectionResetError, socket.timeout):
                continue

            except json.decoder.JSONDecodeError:
                self._print("Failed receiving message: JSONDecodeError")
                continue

            except ConnectionAbortedError:
                self._print("Connection closed")
                return

    def send_msg(self, msg: dict, msg_type: str | None = "shoot") -> None:
        """
        Send a message to the server

        :param msg: Message to send to the server
        :param msg_type: Type of the message to send (e.g: respawn)
        """
        msg_dict = {"type": msg_type, "content": msg}
        msg_str = json.dumps(msg_dict)
        msg_byte = msg_str.encode(ENCRYPTION)

        self.send(msg_byte)

    def shoot(self, msg: dict) -> None:
        """
        Send a shoot event to the server or just use send_msg

        :param msg: Dictonary to send
        """
        self.send_msg(msg)

    def respawn(self) -> None:
        """
        Send a respawn event to the server or just use send_msg
        """
        self.send_msg({}, "respawn")

    def ping(self, timeout: float | None = 1) -> int:
        """
        Returns the ping

        :param timeout: Timeout in seconds
        :return: Ping in milliseconds
        """

        self.send_msg({}, "PING")
        self.__ping_trigger = 1
        time_start = time()

        while self.__ping_trigger == 1:
            if time()-time_start > timeout:
                raise TimeoutError("Ping-Pong was not sucessfull in time")
        ping: int = int((time()-time_start)*1000)
        self._print(f"PING: {ping}")
        return ping

    def _print(self, *msg: any) -> None:
        """
        Only print if debug mode is on

        :param msg: Messages to print
        """
        if self.debug_mode:
            print("CLIENT:", *msg)

    def end(self) -> None:
        """
        End the Communication-Thread and close the connection
        """
        self.__running = False
        self.close()


if __name__ == "__main__":
    cl = Client(SERVER_IP, PORT, debug_mode=True)
    print("\n>>> Client - CMD - Control <<<")
    print("Commands: ")
    print(" - send_data(msg)    |   Send a message to the server")
    print(" - received_msg      |   Returns the oldest received message")
    while True:
        cmd_input = input(">>> ")
        exec(f"cl.{cmd_input}")
