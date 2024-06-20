import socket
import time
import argparse


# 解析命令行参数
parser = argparse.ArgumentParser(description='UDP Client for measuring RTT.')
parser.add_argument('SERVER_IP', type=str, help='Server IP address')
parser.add_argument('SERVER_PORT', type=int, help='Server port number')
args = parser.parse_args()

# 从命令行参数中获取服务端IP和端口
SERVER_IP = args.SERVER_IP
SERVER_PORT = args.SERVER_PORT

# 创建UDP套接字
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(0.1)  # 设置超时时间为100ms

# 发送12个请求数据包
sent_packets = 0
received_packets = 0
rtt_sum = 0
max_rtt = 0
min_rtt = float('inf')
rtt_values = []

first_response_time = None
last_response_time = None

seq_no = 1
version = 2

while seq_no <= 12:
    retries = 2  # 最多重传两次
    while retries>=0:
        # 构造请求报文
        content = 'XSWL' * 50 
        request = seq_no.to_bytes(2, byteorder='big') + version.to_bytes(1, byteorder='big') + content.encode()
        client_socket.sendto(request, (SERVER_IP, SERVER_PORT)) # 通过UDP协议将请求报文发送到指定的服务器IP和端口
        sent_packets += 1
        sent_time = time.perf_counter()#能获得更高精度
        try:
            # 接收响应报文
            data, addr = client_socket.recvfrom(1024)
            received_time = time.perf_counter()#记录响应时间
            received_packets += 1
    
            # 解析响应报文
            resp_seq_no = int.from_bytes(data[:2], byteorder='big')
            resp_version = int.from_bytes(data[2:3], byteorder='big')
            server_time = data[3:].decode().strip()
            print(f'seq_no:{resp_seq_no},server_time:{server_time}')

            
            # 计算RTT
            rtt = (received_time - sent_time) * 1000  # 转换为毫秒
            rtt_sum += rtt
            rtt_values.append(rtt)
            max_rtt = max(max_rtt, rtt)
            min_rtt = min(min_rtt, rtt)
    
            # 记录服务器响应时间
            if first_response_time is None:
                first_response_time=received_time
                last_response_time = first_response_time  
            else:
                last_response_time=received_time

            break#成功收到响应，退出循环
        
        except socket.timeout:  # 处理超时
            print(f'sequence no {seq_no},Request timed out')
            retries -= 1
            
        if retries<0:
            break#次数用完，退出循环
    seq_no += 1

# 计算丢包率 (百分比: 1 - 接收到的UDP包数 / 发送的UDP包数)
drop_rate = 1 - (received_packets / sent_packets)
print(f'send:{sent_packets},rec:{received_packets}')

# 计算RTT统计值
avg_rtt = rtt_sum / received_packets  # 平均RTT
rtt_variance = sum((rtt - avg_rtt) ** 2 for rtt in rtt_values) / received_packets  # 方差
rtt_std_dev = rtt_variance ** 0.5  # 标准差

# 输出汇总信息
print('\n===== 汇总 =====')
print(f'接收到的packets数目: {received_packets}')
print(f'丢包率: {drop_rate * 100:.2f}%')
print(f'最大RTT: {max_rtt:.2f} ms')
print(f'最小RTT: {min_rtt:.2f} ms')
print(f'平均RTT: {avg_rtt:.2f} ms')
print(f'RTT的标准差: {rtt_std_dev:.2f} ms')
time_diff = (last_response_time - first_response_time)* 1000
print(f'Server的整体响应时间: {time_diff:.2f}ms')  # server最后一次response的系统时间与第一次response的系统时间之差

# 关闭套接字，结束交互
client_socket.close()
