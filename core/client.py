"""
core/client.py

Client-class for cummunication with the server

Author: MelonenBuby
Date:   29.06.2022
"""


################################################################################
#                                Import Modules                                #
################################################################################
from traceback import print_exc
import struct
from threading import Thread
import socket
import json

################################################################################
#                           Constants / Settings                              #
################################################################################

SERVER_IP: str = "127.0.0.1"  # 192.168.0.138
ENCRYPTION: str = "UTF-8"
PORT: int = 8888


################################################################################
#                                   Client                                     #
################################################################################

class Client(socket.socket):
    __received_msg: list[dict]
    package_size: int
    debug_mode: bool
    running: bool
    ID: str

    def __init__(self, server_ip: str, port: int, debug_mode: bool | None = False,
                 package_size: int | None = 1024) -> None:
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

        self.package_size = package_size
        self.__received_msg = []
        self.running = True
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
        Returns the oldest received message and deletes it's caching
        :return: Dictonary of the message or none if there is no new messages
        """

        try:
            rec_data = self.__received_msg[0]
            del self.__received_msg[0]
            return rec_data
        except IndexError:
            return None

    def shoot(self, msg: dict) -> None:
        """
        Send a message to the server

        :param msg: Dictonary to send
        """
        mes = {
            "type": "shoot",
            "content": msg
        }

        msg_str = json.dumps(mes)
        msg_byte = msg_str.encode(ENCRYPTION)

        self.send(msg_byte)

    def respawn(self) -> None:
        """
        Send a respawn event to the server
        """
        mes = {
            "type": "respawn"
        }

        msg_str = json.dumps(mes)
        msg_byte = msg_str.encode(ENCRYPTION)

        self.send(msg_byte)

    def __receive(self) -> None:
        """
        Receives messages from the server in packages and saves them
        """

        first: bool = True
        recv: bool = False
        data = bytearray()
        while self.running:
            try:
                msg_byte = self.recv(1)  # receive message length
                if not recv and msg_byte == b'@':
                    recv = True
                elif recv and msg_byte != b"#":
                    data.extend(msg_byte)
                    # print("EXTEND", msg_byte.decode(ENCRYPTION))
                elif recv:
                    msg_str = data.decode(ENCRYPTION)
                    recv = False
                    data = bytearray()
                    try:
                        if first:
                            first = False
                            self.ID = msg_str
                            self._print(f"GOT ID: {self.ID}")
                        else:
                            msg_dic = json.loads(msg_str)
                            self.__received_msg.append(msg_dic)
                        print("SUCCESS")
                    except (ConnectionResetError, struct.error, socket.timeout, json.decoder.JSONDecodeError) as error:
                        print("LOST", error)
                        print_exc()
                        continue

            except socket.timeout:
                continue

    def end(self) -> None:
        """
        End the Communication-Thread and close the connection
        """

        self.running = False
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
