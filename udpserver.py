import socket
import random
import time

# 服务端IP和端口
SERVER_IP = '127.0.0.1'
SERVER_PORT = 40824

# 创建UDP套接字
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
print(f'Server is listening on {SERVER_IP}:{SERVER_PORT}')

# 丢包率
DROP_RATE = 0.4

while True:
    # 接收客户端发送的数据
    data, addr = server_socket.recvfrom(1024)

    # 解析数据包
    seq_no = int.from_bytes(data[:2], byteorder='big')
    version = int.from_bytes(data[2:3], byteorder='big')
    content = data[3:].decode()

    # 模拟丢包
    if random.random() < DROP_RATE:
        print(f'Packet {seq_no} dropped')
        continue

    # 构造响应报文
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    response_content = current_time.ljust(200)#填充至200Byte
    response = seq_no.to_bytes(2, byteorder='big') + version.to_bytes(1, byteorder='big') + response_content.encode()
    server_socket.sendto(response, addr)
    print(f'Sent response for packet {seq_no}: {response_content}')