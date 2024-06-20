import socket
import threading

# 服务器配置
HOST = ''  # 监听所有IP地址
PORT = 8000  # 监听端口号

# 创建TCP套接字
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)  # 最大连接数为5
print(f'服务器正在 {HOST}:{PORT} 上监听...')

def handle_client(conn, addr):
    print(f'{addr} 已连接')
    try:
        # 接收初始化报文
        remaining_bytes = b''
        while True:
            init_msg = conn.recv(1024)
            if not init_msg:
                break
            remaining_bytes += init_msg
            if len(remaining_bytes) >= 5:
                msg_type, n_blocks = remaining_bytes[:1], int.from_bytes(remaining_bytes[1:5], byteorder='big')
                remaining_bytes = remaining_bytes[5:]
                break
        print(f'从 {addr} 收到 {msg_type} 报文, n_blocks={n_blocks}')

        # 发送确认报文
        agree_msg = b'\x02' + n_blocks.to_bytes(4, byteorder='big')
        conn.sendall(agree_msg)
        print(f'已向 {addr} 发送确认报文')

        # 处理反转请求
        for i in range(n_blocks):
            remaining_bytes = b''
            while True:
                req_msg = conn.recv(1024)
                if not req_msg:
                    break
                remaining_bytes += req_msg
                if len(remaining_bytes) >= 5:
                    msg_type, data_len = remaining_bytes[:1], int.from_bytes(remaining_bytes[1:5], byteorder='big')
                    if len(remaining_bytes) >= data_len + 5:
                        data = remaining_bytes[5:5+data_len]
                        remaining_bytes = remaining_bytes[5+data_len:]
                        break

            reversed_data = data[::-1]
            resp_msg = b'\x04' + len(reversed_data).to_bytes(4, byteorder='big') + reversed_data
            conn.sendall(resp_msg)
            print(f'已向 {addr} 发送第 {i+1} 块反转数据')
    except Exception as e:
        print(f'错误: {e}')
    finally:
        conn.close()
        print(f'{addr} 已断开连接')

# 主循环
while True:
    conn, addr = server_socket.accept()
    client_thread = threading.Thread(target=handle_client, args=(conn, addr))
    client_thread.start()