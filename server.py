import socket
import sys
from queue import Queue

clients = {}
NAME_POS = 0
MASSAGES_POS = 1


def ensure_and_get_name_from_first_massage(data_str):
    if data_str[:2] != '1 ' or len(data_str) < 3:
        return None
    return data_str[2:]


def get_all_waiting_massages_to(client_addr):
    massages_arr = []
    curr_client_massages = clients[client_addr][MASSAGES_POS]
    while not curr_client_massages.empty():
        massages_arr.append(curr_client_massages.get())
    return '\n'.join(massages_arr)


def add_massage_to_all_clients(massage, except_for=None):
    for client in clients.values():
        if except_for is None or clients[except_for] != client:
            client[MASSAGES_POS].put(massage)


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ip = sys.argv[1]
port = sys.argv[2]

s.bind((ip, int(port)))

while True:
    data, addr = s.recvfrom(1024)
    data = data.decode()  # moving to str
    massage_to_client = ''
    if addr in clients:  # the client is in the database, we need to validate and handle his request.
        if data[0] == '1':
            massage_to_client = 'Illegal request'
        elif data[0] == '2' and data[1] == ' ' and len(data) > 2:
            massage_to_client = get_all_waiting_massages_to(addr)
            add_massage_to_all_clients(clients[addr][NAME_POS] + ': ' + data[2:], except_for=addr)
        elif data[0] == '3' and data[1] == ' ' and len(data) > 2:
            massage_to_client = get_all_waiting_massages_to(addr)
            old_name = clients[addr][NAME_POS]
            new_name = data[2:]
            clients[addr][NAME_POS] = new_name
            add_massage_to_all_clients(old_name + ' changed his name to ' + new_name, except_for=addr)
        elif data == '4':
            deleted_name = clients[addr][NAME_POS]
            del clients[addr]
            add_massage_to_all_clients(deleted_name + ' has left the group')
        elif data == '5':
            massage_to_client = get_all_waiting_massages_to(addr)
        else:  # illegal massage format.
            massage_to_client = 'Illegal request'
    else:  # the client is new
        name = ensure_and_get_name_from_first_massage(data)
        if name is None:
            massage_to_client = 'Illegal request'
        else:
            add_massage_to_all_clients(name + ' has joined')
            massage_to_client = ', '.join([client_info[NAME_POS] for client_info in clients.values()])
            clients[addr] = [name, Queue()]

    s.sendto(massage_to_client.encode(), addr)
