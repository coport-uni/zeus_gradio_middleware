# Zeus 개발
## Zeus 문제 해결
1. ssh-rsa 문제
	* https://jsikim1.tistory.com/336
	```
	ssh -o "HostKeyAlgorithms ssh-rsa" i611usr@192.168.0.23
	```

2. Vscode 문제
	1. MobaXterm과 병행해서 활용
	2. 리눅스(https://www.timesys.com/) 익숙해지기
	3. Unicode간 통신
3. 인터넷 / Root 안됨
## Zeus 인터페이스 개발
* https://mcc96.tistory.com/58
* https://local-pipe-555.notion.site/1f851d8f7693800fa069d8a4f9b24ef9?pvs=4
```python title=ZeusServer  
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
```

```python title=ZeusClient
import socket
import time
import gradio as gr

class ZeusClient():
    def __init__(self):
        """
        Initialize server setup
        """
        self.server_address = "192.168.0.23"
        self.server_port = 5555

    def send_client_command(
            self, order_type, order_data_joint0, order_data_joint1, order_data_joint2, \
            order_data_joint3, order_data_joint4, order_data_joint5):
        """
        Communicating server and collect response from server
        """
        input_list = (
                order_data_joint0,order_data_joint1,\
                order_data_joint2,order_data_joint3,\
                order_data_joint4,order_data_joint5)
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_address, self.server_port))
            request = "{}&&{}&&{}&&{}&&{}&&{}&&{}".format(order_type, input_list[0],input_list[1],input_list[2],input_list[3],input_list[4],input_list[5])
            self.client_socket.send(request.encode("utf-8"))
            response = self.client_socket.recv(1024).decode("utf-8")
            print("서버 : {}".format(response))
            return response

        except Exception as e:
                print("Error: {}".format(e))

        finally:
                print("Connection closed")
                self.client_socket.close()

    def run_gui_interface(self):

        with gr.Blocks() as demo:

            gr.Markdown("Zeuscontorl-Joint")
            order_type_joint = gr.Dropdown(["move_joint", "position_joint"],label="order_type_joint")
            order_data_joint0 = gr.Slider(-360,360, value=0, step=2,label="j1")
            order_data_joint1 = gr.Slider(-360,360, value=0, step=2,label="j2")
            order_data_joint2 = gr.Slider(-360,360, value=0, step=2,label="j3")
            order_data_joint3 = gr.Slider(-360,360, value=0, step=2,label="j4")
            order_data_joint4 = gr.Slider(-360,360, value=0, step=2,label="j5")
            order_data_joint5 = gr.Slider(-360,360, value=0, step=2,label="j6")
            txt_joint = gr.Textbox(value="",label="결과")
            button_joint = gr.Button(value="실행")
            button_joint.click(self.send_client_command, inputs=[order_type_joint, order_data_joint0, order_data_joint1, order_data_joint2, \
                                                                 order_data_joint3, order_data_joint4, order_data_joint5], outputs=[txt_joint])

            gr.Markdown("Zeuscontorl-EEF")
            order_type_eef = gr.Dropdown(["move_eef", "position_eef"],label="order_type_eef")
            order_data_eef0 = gr.Slider(-100,100, value=0, step=1,label="x")
            order_data_eef1 = gr.Slider(-100,100, value=0, step=1,label="y")
            order_data_eef2 = gr.Slider(-100,100, value=0, step=1,label="z")
            order_data_eef3 = gr.Slider(-100,100, value=0, step=1,label="u")
            order_data_eef4 = gr.Slider(-100,100, value=0, step=1,label="v")
            order_data_eef5 = gr.Slider(-100,100, value=0, step=1,label="w")
            eef_list = (
                order_data_joint0,order_data_joint1,\
                order_data_joint2,order_data_joint3,\
                order_data_joint4,order_data_joint5)
            txt_eef = gr.Textbox(value="",label="결과")
            button_eef = gr.Button(value="실행")
            button_eef.click(self.send_client_command, inputs=[order_type_eef, order_data_eef0, order_data_eef1, order_data_eef2, \
                                                               order_data_eef3, order_data_eef4, order_data_eef5], outputs=[txt_eef])


        demo.launch(share=True)

def main():
    zc = ZeusClient()
    zc.run_gui_interface()
    # zc.send_client_command("position_joint", (0,0,0,0,0,0))
    # zc.send_client_command("eef_joint", (0,0,0,0,0,0))
    # while True:
        # zc.send_client_command("move_joint", (10,0,0,0,0,0))
        # time.sleep(0.5)
        # zc.send_client_command("move_eef", (30,0,0,0,0,0))

     
if __name__ == "__main__":
    main()
```

# 결과
* 첨부예정

# Gripper + Modbus 통합
## Setup
* https://discuss.python.org/t/installing-pip-on-an-old-linux-machine-without-internet/13317
* https://pypi.org/project/minimalmodbus/0.6/#description
* https://ding-dong-in-future.tistory.com/296
* 
```bash
# pip install
python pip-20.3.4-py2.py3-none-any.whl/pip install pip-20.3.4-py2.py3-none-any.whl

# pip install modbus
pip download minimalmodbus -d "C:\Users\USER_55_DeepLearning\Desktop\minimalmodbus0.6"
python -m pip install --no-index -f sungwoo_files/minimalmodbus0.6 minimalmodbus

```

* Root 패스워드 없이는 진행불가? => 라즈베리로 통합제어기 설계
* ZeusClient => ZEUS, RPI로 각각?
![[Pasted image 20250625184917.png]]
```bash
python -m venv zeus --system-site-packages
source zeus/bin/activate
pip install tqdm
pip install minimalmodbus
```
## Code
* 기존 코드에 통합을 목표로
```python title=HandEServer
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
        self.gripper.write_registers(self.output_address, [0x0900, goal_position, (goal_speed << 8) | goal_force])
        time.sleep(2)

        return str(self.get_hande_status())

class HandEServer:
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
```

```python title=ZeusHandEClient
import socket
import time
import gradio as gr

class HandEClient():
    def __init__(self):
        """
        Initialize server setup
        """
        self.server_address = "192.168.0.33"
        self.server_port = 5555

    def send_client_command(self, goal_position):
        """
        Communicating server and collect response from server
        """
        goal_speed = 255
        goal_force = 255
        input_list = (goal_position, goal_speed, goal_force)
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_address, self.server_port))
            request = "{}&&{}&&{}".format(input_list[0],input_list[1],input_list[2])
            self.client_socket.send(request.encode("utf-8"))
            response = self.client_socket.recv(1024).decode("utf-8")
            print("서버 : {}".format(response))

            return response

        except Exception as e:
                print("Error: {}".format(e))

        finally:
                print("Connection closed")
                self.client_socket.close()

class ZeusClient():
    def __init__(self):
        """
        Initialize server setup
        """
        self.server_address = "192.168.0.23"
        self.server_port = 5555

    def send_client_command(
            self, order_type, order_data_joint0, order_data_joint1, order_data_joint2, \
            order_data_joint3, order_data_joint4, order_data_joint5):
        """
        Communicating server and collect response from server
        """
        input_list = (
                order_data_joint0,order_data_joint1,\
                order_data_joint2,order_data_joint3,\
                order_data_joint4,order_data_joint5)
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_address, self.server_port))
            request = "{}&&{}&&{}&&{}&&{}&&{}&&{}".format(order_type, input_list[0],input_list[1],input_list[2],input_list[3],input_list[4],input_list[5])
            self.client_socket.send(request.encode("utf-8"))
            response = self.client_socket.recv(1024).decode("utf-8")
            print("서버 : {}".format(response))
            
            return response

        except Exception as e:
                print("Error: {}".format(e))

        finally:
                print("Connection closed")
                self.client_socket.close()

def run_gui_interface():
        zc = ZeusClient()
        hc = HandEClient()

        with gr.Blocks() as demo:

            gr.Markdown("Zeuscontorl-Joint")
            order_type_joint = gr.Dropdown(["move_joint", "position_joint"],label="order_type_joint")
            order_data_joint0 = gr.Slider(-360,360, value=0, step=2,label="j1")
            order_data_joint1 = gr.Slider(-360,360, value=0, step=2,label="j2")
            order_data_joint2 = gr.Slider(-360,360, value=0, step=2,label="j3")
            order_data_joint3 = gr.Slider(-360,360, value=0, step=2,label="j4")
            order_data_joint4 = gr.Slider(-360,360, value=0, step=2,label="j5")
            order_data_joint5 = gr.Slider(-360,360, value=0, step=2,label="j6")
            txt_joint = gr.Textbox(value="",label="결과")
            button_joint = gr.Button(value="Zeus 실행")
            button_joint.click(zc.send_client_command, inputs=[order_type_joint, order_data_joint0, order_data_joint1, order_data_joint2, \
                                                                 order_data_joint3, order_data_joint4, order_data_joint5], outputs=[txt_joint])
                                                                 
            gr.Markdown("Zeuscontorl-EEF")
            order_type_eef = gr.Dropdown(["move_eef", "position_eef"],label="order_type_eef")
            order_data_eef0 = gr.Slider(-100,100, value=0, step=1,label="x")
            order_data_eef1 = gr.Slider(-100,100, value=0, step=1,label="y")
            order_data_eef2 = gr.Slider(-100,100, value=0, step=1,label="z")
            order_data_eef3 = gr.Slider(-100,100, value=0, step=1,label="u")
            order_data_eef4 = gr.Slider(-100,100, value=0, step=1,label="v")
            order_data_eef5 = gr.Slider(-100,100, value=0, step=1,label="w")
            txt_eef = gr.Textbox(value="",label="결과")
            button_eef = gr.Button(value="실행")
            button_eef.click(zc.send_client_command, inputs=[order_type_eef, order_data_eef0, order_data_eef1, order_data_eef2, \
                                                               order_data_eef3, order_data_eef4, order_data_eef5], outputs=[txt_eef])
            gr.Markdown("Zeuscontorl-Gripper")
            order_data_gripper = gr.Slider(0,255, value=0, step=5,label="gripper")
            txt_gripper = gr.Textbox(value="",label="결과")
            button_gripper = gr.Button(value="Zeus 실행")
            button_gripper.click(hc.send_client_command, inputs=[order_data_gripper], outputs=[txt_gripper])


        demo.launch(share=True)

def main():
    run_gui_interface()
    # zc.send_client_command("position_joint", (0,0,0,0,0,0))
    # zc.send_client_command("eef_joint", (0,0,0,0,0,0))
    # while True:
        # zc.send_client_command("move_joint", (10,0,0,0,0,0))
        # time.sleep(0.5)
        # zc.send_client_command("move_eef", (30,0,0,0,0,0))

     
if __name__ == "__main__":
    main()
```
##  결과
