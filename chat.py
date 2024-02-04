import gradio as gr
import socket
import threading

# 服务器地址和端口
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 9999

def handle_client(client_socket, client_address):
    print(f"[+] {client_address} 连接成功.")
    while True:
        try:
            message = client_socket.recv(1024).decode()
            print(message)
        except Exception as e:
            print(f"[-] 错误: {e}")
            break

    print(f"[-] {client_address} 断开连接.")
    client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"[*] 正在监听 {SERVER_HOST}:{SERVER_PORT} ...")

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

def send_message(message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    client_socket.send(message.encode())

    client_socket.close()

iface = gr.Interface(fn=send_message, inputs="text", outputs=None, title="实时通讯应用", description="在此输入消息并发送")
iface.launch(share=True)

# 启动服务器
start_server()
