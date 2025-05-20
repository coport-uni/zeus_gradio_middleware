#!/usr/bin/python
# -*- coding: utf-8 -*-

from i611_MCS import *
from i611_extend import *
from i611_io import *
from teachdata import *
from rbsys import *
from i611_common import *
from i611shm import *
# from ZeusServer import ZeusServer

import socket
import os
import time

os.system("python error_clear.py")
rb = i611Robot()
_BASE = Base()

rb.open()
IOinit(rb)

data = Teachdata("teach_data")
m = MotionParam(jnt_speed=10, lin_speed=70)
rb.motionparam(m)

class ZeusInterface:
    def __init__(self):
        """
        Initialize ZEUS base
        """
        self.rb = rb
        print("ZEUS Interface Running")

    # def __del__(self):
    #     """
    #     Destructing ZEUS base
    #     """
    #     open("end", "w").close()
    #     self.rb.close()

    def get_joint_position(self):
        """
        get joint data(list)
        """
        a = self.rb.getjnt()
        output = a.jnt

        return output

    def get_eef_position(self):
        """
        get eef data(list)
        """
        a = self.rb.getpos()
        output = a.pos
        
        return output
    
    def run_joint_position(self, zeus_input):
        """
        run joint data(list)
        """
        target = Joint(
            zeus_input[0],zeus_input[1],zeus_input[2], \
            zeus_input[3],zeus_input[4],zeus_input[5])
        self.rb.move(target)
        message = "Moving to joint position {}".format(str(zeus_input))

        return message

    def run_eef_position(self, zeus_input):
        """
        run eef data(list)
        Move to relative position for better uses.
        """
        current_eef_position = self.get_eef_position()
        target = Position(
            float(current_eef_position[0] + zeus_input[0]),float(current_eef_position[1] + zeus_input[1]),\
            float(current_eef_position[2] + zeus_input[2]),float(current_eef_position[3] + zeus_input[3]), \
            float(current_eef_position[4] + zeus_input[4]),float(current_eef_position[5] + zeus_input[5]))
                    
        self.rb.move(target)
        message = "Moving to relative eef position {}".format(str(zeus_input))
        
        return message

    def run_home(self):
        self.rb.home()
        message = "Moving to home position"
        
        return message

    def run_command(self, order_type, order_data):
        time.sleep(1)
        if order_type=="move_joint":
            message = self.run_joint_position(order_data)
            return(message)

        elif order_type=="move_eef":
            message = self.run_eef_position(order_data)
            return(message)
    
        elif order_type=="position_joint":
            return (str(self.get_joint_position()))
        
        elif order_type=="position_eef":
            return (str(self.get_eef_position()))
        
        elif order_type=="move_home":
            return (str(self.run_home()))

        else:
            print("error!")

class ZeusServer:
    def __init__(self):
        """
        Initialize server setup
        """
        self.host = "0.0.0.0"
        self.port = 5555
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        
        print("Server Running at {}:{}".format(self.host,self.port))

    def run_client_command(self):
        """
        Running server and collect response from client
        """

        zi = ZeusInterface()

        while True:
            self.server_socket.listen(5)
            self.client_socket, self.client_address = self.server_socket.accept()
            print("Client {} connected.".format(self.client_address))
            
            try:
                data = self.client_socket.recv(1024).decode("utf-8")
                # print(data)
                if not data:
                    continue

                parts = data.split("&&")
                if len(parts) != 0:
                    order_type = parts[0]
                    order_data = (
                        float(parts[1]),float(parts[2]), float(parts[3]), \
                        float(parts[4]),float(parts[5]), float(parts[6]))
                    
                    # for i in range(len(parts)):
                    #     print(parts[i+1], type(float(parts[i+1])))
                    #     order_data[i] = float(parts[i+1])
                    
                    # array = order_data.split(" ").split("(").split(")").split(",")
                    # print(array)

                    #print(type(order_data))
                    # data = map(float, order_data)
                    # print(type(order_data), order_data)
                    # array = order_data.split().split(",").split("(").split(")")
                    # print(array)


                    response = zi.run_command(order_type,order_data)
    
                else:
                    response = "Invalid operation"

                self.client_socket.send(response.encode("utf-8"))

                return order_type, order_data

            except Exception as e:
                print("Error: {}".format(e))

            finally:
                print("Connection closed")
                self.client_socket.close()

def main():
    """
    Main function
    """
    zs = ZeusServer()
    
    while True:
        zs.run_client_command()
        
if __name__ == "__main__":
    main()