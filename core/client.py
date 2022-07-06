"""
MelonenBuby 2022

Author: Lukas Krahbichler
Date:   29.06.2022
"""


################################################################################
#                                Import Modules                                #
################################################################################

from threading import Thread
import socket
import time
import json


################################################################################
#                           Constants / Settings                              #
################################################################################

SERVER_IP: str = "127.0.0.1"
ENCRYPTION: str = "UTF-32"
PORT: int = 8888


################################################################################
#                                   Client                                     #
################################################################################

class Client(socket.socket):
    __received_msg: list[dict]
    debug_mode: bool
    ID: str

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
        self.ID = ""

        self.connect((server_ip, port))
        Thread(target=self.__receive, args=()).start()

    def _print(self, *msg: any) -> None:
        """
        Only print if debug mode is on

        :param msg: Messages to print
        """

        if self.debug_mode:
            print("CLIENT:", *msg)

    @property
    def received_msg(self) -> dict | None:
        """
        Returns the oldest received message
        :return: Dictonary of the message or none if there is no new messages
        """

        try:
            rec_data = self.__received_msg[0]
            del self.__received_msg[0]
            return rec_data
        except IndexError:
            return None

    def send_data(self, msg: dict) -> None:
        """
        Send a message to the server

        :param msg: Dictonary to send
        """

        msg_str = json.dumps(msg)
        msg_byte = msg_str.encode(ENCRYPTION)

        self.send(msg_byte)

    def __receive(self) -> None:
        """
        Receives messages from the server and saves them
        """
        first = True

        while True:
            msg = self.recv(1024)
            if msg == b"":
                self.close()
                return
            else:
                msg_str = msg.decode(ENCRYPTION)
                if first:
                    first = False
                    self.ID = msg_str
                    self._print(f"GOT ID: {self.ID}")

                else:
                    try:
                        msg_dic = json.loads(msg_str)
                        self.__received_msg.append(msg_dic)

                    except json.JSONDecodeError:
                        continue


if __name__ == "__main__":
    cl = Client(SERVER_IP, PORT, debug_mode=True)
    print("\n>>> Client - CMD - Control <<<")
    print("Commands: ")
    print(" - send_data(msg)    |   Send a message to the server")
    print(" - received_msg      |   Returns the oldest received message")
    while True:
        cmd_input = input(">>> ")
        exec(f"cl.{cmd_input}")
