import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip = sys.argv[1]
port = sys.argv[2]
while True:
    value = input()
    s.sendto(value.encode(), (ip, int(port)))
    data, addr = s.recvfrom(1024)
    if len(data) > 0:
        print(data.decode())  # decoding to str
