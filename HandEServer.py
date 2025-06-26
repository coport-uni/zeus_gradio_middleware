import serial
import time
import os
import socket
import minimalmodbus
from tqdm import tqdm

# RPI = 192.168.0.33
# ZEUS = 192.168.0.23

class HandEController():
    def __init__(self):
        '''
        This function initialize communication with HandE.

        Input: None
        Output: None
        '''
        # os.system("dmesg | grep tty")
        self.gripper = minimalmodbus.Instrument("/dev/ttyUSB1", 9)
        serialconfig_gripper = self.gripper.serial
        serialconfig_gripper.baudrate = 115200
        serialconfig_gripper.bytesize = 8
        serialconfig_gripper.stopbits = 1
        serialconfig_gripper.parity = serial.PARITY_NONE
        serialconfig_gripper.timeout = 1

        self.output_address = 1000
        self.input_address = 2000

        self.gripper.mode = minimalmodbus.MODE_RTU
        self.gripper.clear_buffers_before_each_transaction = True

    def get_hande_status(self):
        '''
        This function read register from HandE. It uses bit-shifting operation for parsing.

        Input: None
        Output: list
        '''
        status_register = self.gripper.read_registers(self.input_address, 3)
        register0, register1, register2 = status_register

        status_activate = register0 & 0x01
        status_movement = (register0 >> 3) & 0x01
        status_standby = (register0 >> 3) & 0x01
        status_object = (register0 >> 6) & 0x03
        status_gripper = (register2 >> 8) & 0xFF

        # error_gripper = register1 & 0x000F
        # error_controller = (register1 >> 4) & 0x000F
        # current_gripper = register2 & 0x00FF

        status_gripper = (status_activate, status_movement, status_standby, status_object, status_gripper)

        return status_gripper
    
    def initialize_hande(self):
        '''
        This function initalize hande

        Input: None
        Output: None
        '''
        reset_activation_byte = 0x0000
        run_activation_byte = 0x0100

        self.gripper.write_registers(self.output_address, [reset_activation_byte, 0, 0])
        time.sleep(2)
        self.gripper.write_registers(self.output_address, [run_activation_byte, 0, 0])
        time.sleep(2)

        print("Initialization Complete")

    def run_hande(self, goal_position, goal_speed, goal_force):
        '''
        This function run hande to expected location with supplied parameters

        Input: None
        Output: list
        '''
        run_action_byte = 0x0900
        
        self.gripper.write_registers(self.output_address, [run_action_byte, goal_position, (goal_speed << 8) | goal_force])
        time.sleep(2)

        return str(self.get_hande_status())

class HandEServer:
    def __init__(self):
        """
        Initialize server setup
        
        Input: None
        Output: None
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
        
        Input: None
        Output: None
        """
        hc = HandEController()

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
                    goal_position = int(parts[0])
                    goal_speed = int(parts[1])
                    goal_force = int(parts[2])

                    response = hc.run_hande(goal_position, goal_speed, goal_force)
    
                else:
                    response = "Invalid operation"

                self.client_socket.send(response.encode("utf-8"))

            except Exception as e:
                print("Error: {}".format(e))

            finally:
                print("Connection closed")
                self.client_socket.close()

def main():
    """
    Main function
    
        Input: None
        Output: None
    """
    # hc = HandEController()
    # hc.initialize_hande()
    # for i in tqdm(range(10)):
    #     hc.run_hande(0,255,255)
    #     hc.run_hande(255,255,255)
    hs = HandEServer()
    while True: 
        hs.run_client_command()

if __name__ == "__main__":
    main()