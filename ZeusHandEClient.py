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