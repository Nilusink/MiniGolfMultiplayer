"""
core/client.py

Client-class for cummunication with the server

Author: MelonenBuby
Date:   29.06.2022
"""


################################################################################
#                                Import Modules                                #
################################################################################

from core.debug import debug, all_methods
from threading import Thread
from time import time
import socket
import json

################################################################################
#                           Constants / Settings                              #
################################################################################

SERVER_IP: str = "192.168.0.138"
LOCAL_IP: str = "127.0.0.1"
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

@all_methods(debug)
class Client(socket.socket):
    __received_msg: list[dict]
    __ping_trigger: int
    debug_mode: int
    __running: bool
    __game_map: dict
    __ID: str

    def __init__(self, server_ip: str, port: int, debug_mode: int | None = 0) -> None:
        """
        Client for communicating between game calculating and game GUI

        :param server_ip: IP of the server
        :param port: Port
        :param debug_mode: 0 - NoDebug, 1 - OnlyImportantInformations, 2 - LightDebug, 3 - FullDebug
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
                            self._print("GOT MSG", msg_content, min_debug=2)
                            self.__received_msg.append(msg_content)
                        case "ID":
                            self._print("GOT ID", msg_content)
                            self.__ID = msg_content
                        case "map":
                            self._print("GOT MAP", msg_content)
                            self.__game_map = msg_content
                        case "PONG":
                            self._print("GOT PONGED", msg_content, min_debug=2)
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
        msg_dict = {"type": msg_type, "content": msg, "time": time()}
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

    def _print(self, *msg: any, min_debug: int | None = 1) -> None:
        """
        Only print if debug mode is on

        :param msg: Messages to print
        :param min_debug: 1 - OnlyImportantInformations, 2 - LightDebug, 3 - FullDebug
        """
        if self.debug_mode >= min_debug:
            print("CLIENT:", *msg)

    def end(self) -> None:
        """
        End the Communication-Thread and close the connection
        """
        self.__running = False
        self.close()


if __name__ == "__main__":
    cl = Client(LOCAL_IP, PORT, debug_mode=1)
    print("\n>>> Client - CMD - Control <<<")
    print("Commands: ")
    print(" - send_data(msg)    |   Send a message to the server")
    print(" - received_msg      |   Returns the oldest received message")
    while True:
        cmd_input = input(">>> ")
        exec(f"cl.{cmd_input}")
