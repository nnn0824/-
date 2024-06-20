import socket
import random
import sys

# 检查命令行参数
if len(sys.argv) != 5:
    print(f'用法: {sys.argv[0]} <服务器IP> <服务器端口> <最小块长度> <最大块长度>')
    sys.exit(1)

SERVER_IP = sys.argv[1]
SERVER_PORT = int(sys.argv[2])
MIN_BLOCK_LEN = int(sys.argv[3])
MAX_BLOCK_LEN = int(sys.argv[4])

FILE_PATH = 'test.txt'
OUTPUT_PATH = 'reversed_test.txt'

# 创建TCP套接字
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))
print(f'已连接到 {SERVER_IP}:{SERVER_PORT}')

try:
    # 读取文件内容
    with open(FILE_PATH, 'r') as f:
        file_content = f.read()

    # 生成数据块长度列表
    data_len = len(file_content)
    block_lengths = []
    remaining_len = data_len
    while remaining_len > MAX_BLOCK_LEN:
        block_len = random.randint(MIN_BLOCK_LEN, MAX_BLOCK_LEN)
        block_lengths.append(block_len)
        remaining_len -= block_len
    block_lengths.append(remaining_len)

    # 发送初始化报文
    n_blocks = len(block_lengths)
    init_msg = b'\x01' + n_blocks.to_bytes(4, byteorder='big')
    client_socket.sendall(init_msg)
    print(f'已发送初始化报文, n_blocks={n_blocks}')

    # 接收确认报文
    agree_msg = client_socket.recv(1024)
    msg_type, recv_n_blocks = agree_msg[:1], int.from_bytes(agree_msg[1:5], byteorder='big')
    if msg_type != b'\x02' or recv_n_blocks != n_blocks:
        raise Exception('无效的确认报文')
    print('已收到确认报文')

    # 发送反转请求并接收响应
    offset = 0
    reversed_content = ''
    for i, block_len in enumerate(block_lengths):
        data = file_content[offset:offset+block_len]
        req_msg = b'\x03' + len(data).to_bytes(4, byteorder='big') + data.encode()
        client_socket.sendall(req_msg)

        remaining_bytes = b''
        while True:
            resp_msg = client_socket.recv(1024)
            if not resp_msg:
                break
            remaining_bytes += resp_msg
            if len(remaining_bytes) >= 5:
                msg_type, reversed_len = remaining_bytes[:1], int.from_bytes(remaining_bytes[1:5], byteorder='big')
                if len(remaining_bytes) >= reversed_len + 5:
                    reversed_data = remaining_bytes[5:5+reversed_len].decode()
                    remaining_bytes = remaining_bytes[5+reversed_len:]
                    print(f'第 {i+1} 块: {reversed_data}')
                    reversed_content += reversed_data
                    break

        offset += block_len

    # 将反转内容写入到输出文件
    with open(OUTPUT_PATH, 'w') as f:
        f.write(reversed_content)
    print(f'已将反转内容写入到 {OUTPUT_PATH}')

except Exception as e:
    print(f'错误: {e}')
finally:
    client_socket.close()
    print('已断开与服务器的连接')
