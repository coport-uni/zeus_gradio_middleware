import socket
import time
import gradio as gr

class HandEClient():
    def __init__(self):
        """
        Initialize server setup
        
        Input: None
        Output: None
        """
        self.server_address = "192.168.0.33"
        self.server_port = 5555

    def send_client_command(self, goal_position):
        """
        Communicating server and collect response from server
        
        Input: int
        Output: None
        """
        goal_speed = 255
        goal_force = 150
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
         
        Input: None
        Output: None
        """
        self.server_address = "192.168.0.23"
        self.server_port = 5555

    def send_client_command(
            self, order_type, order_data_joint0, order_data_joint1, order_data_joint2, \
            order_data_joint3, order_data_joint4, order_data_joint5):
        """
        Communicating server and collect response from server
         
        Input: None
        Output: None
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

class IntegratedController():
     
    def __init__(self):
        self.zc = ZeusClient()
        self.hc = HandEClient()
         
    def run_gui_interface(self):
        """
        this function runs full gradio
        
        Input: None
        Output: None
        """
        with gr.Blocks() as demo:

            gr.Markdown("Zeuscontrol-Joint")
            order_type_joint = gr.Dropdown(["move_joint", "position_joint"],label="order_type_joint")
            order_data_joint0 = gr.Slider(-360,360, value=0, step=2,label="j1")
            order_data_joint1 = gr.Slider(-360,360, value=0, step=2,label="j2")
            order_data_joint2 = gr.Slider(-360,360, value=0, step=2,label="j3")
            order_data_joint3 = gr.Slider(-360,360, value=0, step=2,label="j4")
            order_data_joint4 = gr.Slider(-360,360, value=0, step=2,label="j5")
            order_data_joint5 = gr.Slider(-360,360, value=0, step=2,label="j6")
            txt_joint = gr.Textbox(value="",label="결과")
            button_joint = gr.Button(value="Zeus 실행")
            button_joint.click(self.zc.send_client_command, inputs=[order_type_joint, order_data_joint0, order_data_joint1, order_data_joint2, \
                                                                 order_data_joint3, order_data_joint4, order_data_joint5], outputs=[txt_joint])
                                                                 
            gr.Markdown("Zeuscontrol-EEF")
            order_type_eef = gr.Dropdown(["move_eef", "position_eef"],label="order_type_eef")
            order_data_eef0 = gr.Slider(-100,100, value=0, step=1,label="x")
            order_data_eef1 = gr.Slider(-100,100, value=0, step=1,label="y")
            order_data_eef2 = gr.Slider(-100,100, value=0, step=1,label="z")
            order_data_eef3 = gr.Slider(-100,100, value=0, step=1,label="u")
            order_data_eef4 = gr.Slider(-100,100, value=0, step=1,label="v")
            order_data_eef5 = gr.Slider(-100,100, value=0, step=1,label="w")
            txt_eef = gr.Textbox(value="",label="결과")
            button_eef = gr.Button(value="실행")
            button_eef.click(self.zc.send_client_command, inputs=[order_type_eef, order_data_eef0, order_data_eef1, order_data_eef2, \
                                                               order_data_eef3, order_data_eef4, order_data_eef5], outputs=[txt_eef])
            gr.Markdown("Zeuscontrol-Gripper")
            order_data_gripper = gr.Slider(0,255, value=0, step=5,label="gripper")
            txt_gripper = gr.Textbox(value="",label="결과")
            button_gripper = gr.Button(value="Zeus 실행")
            button_gripper.click(self.hc.send_client_command, inputs=[order_data_gripper], outputs=[txt_gripper])

            gr.Markdown("Zeuscontrol-Scenario")
            txt_scenario = gr.Textbox(value="",label="결과")
            button_scenario1 = gr.Button(value="1번 시나리오")
            button_scenario1.click(self.run_scenario1, outputs=[txt_scenario])
            button_scenario1 = gr.Button(value="2번 시나리오")
            button_scenario1.click(self.run_open_spectrometer, outputs=[txt_scenario])

        demo.launch(share=True)
    
    def run_order(self, order_type : int, order_data0 : int, order_data1 : int, order_data2 : int, \
                  order_data3 : int, order_data4 : int, order_data5 : int, gripper_data0 : int):
         order_list = ("move_joint", "move_eef", "position_joint", "position_eef")

         self.zc.send_client_command(order_list[order_type], order_data0, order_data1, order_data2, order_data3, order_data4, order_data5)
         time.sleep(1)
         self.hc.send_client_command(gripper_data0)
         time.sleep(2)
         
    def run_initialization(self):
        # Testing successful connection
        message = "Scenario_complete"

        self.run_order(0, 0, 0, 0, 0 ,0 ,0, 250)
        self.run_order(0, 0, 0, 0, 0 ,0 ,0, 0)

        return message

    def run_open_spectrometer(self):
        # Run initialization
        message = self.run_initialization()

        self.run_order(0, 90, 44, 151, 3, -106, -40, 0) # [90.00139232673267, 43.954362623762371, 151.1693224009901, 3.0559251237623761, -106.11803836633662, -39.775061881188122]
        # Turn gripper
        self.run_order(1, 0, 0, 0, 0, 90, 0, 0)

        # Move to gripper to handle
        self.run_order(1, 0, 0, -60, 0, 0, 0, 0)
        self.run_order(1, 0, -75, 0, 0, 0, 0, 0)
        self.run_order(1, 0, 0, 60, 0, 0, 0, 0)

        # Open Spectrometer
        self.run_order(1, -10, 0, 150, 0, 0, 0, 0)
        self.run_order(1, 100, 0, 165, 0, 0, 0, 0)
        self.run_order(1, 145, 0, 50, 0, 0, 0, 0)

        # Hands off from spectrometer
        self.run_order(1, -40, 0, 0, 0, 0, 0, 0)

        return message
    
    def run_scenario1(self):

        # Run initialization
        message = self.run_initialization()

        # Move to pippet station and grap UVcell
        self.run_order(0, 1, 85, 29, 1, -25, -41, 0)
        self.run_order(0, 1, 85, 29, 1, -25, -41, 250)
        #  self.run_order(0, 1, 85, 29, 1, -25, -41, 0)

        # # Move to Spectrommeter
        self.run_order(1, 0, 0, 150, 0, 0, 0, 250)
        self.run_order(1, 0, 500, 0, 0, 0, 0, 250)
        self.run_order(0, 90, 44, 151, 3, -106, -40, 250)

        # Put UVcell to spectrometer
        self.run_order(1, 0, -80, 10, 0, 0, 0, 250)
        self.run_order(1, 155, 0, 0, 0, 0, 0, 250)
        self.run_order(1, 155, 0, -20, 0, 0, 0, 250)
        self.run_order(1, 155, 0, -20, 0, 0, 0, 0) # [78.696163366336634, 45.053372524752476, 125.50595606435643, -8.5080445544554451, -81.68154393564356, -39.385442450495049]

        self.run_order(1, 0, 0, 200, 0, 0, 0, 0)

        return message
         

def main():
    """
    this function is main function
        
    Input: None
    Output: None
    """
    ic = IntegratedController()
    ic.run_gui_interface()

    # self.zc.send_client_command("position_joint", (0,0,0,0,0,0))
    # self.zc.send_client_command("eef_joint", (0,0,0,0,0,0))
    # while True:
        # self.zc.send_client_command("move_joint", (10,0,0,0,0,0))
        # time.sleep(0.5)
        # self.zc.send_client_command("move_eef", (30,0,0,0,0,0))

     
if __name__ == "__main__":
    main()