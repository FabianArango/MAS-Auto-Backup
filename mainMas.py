import socket, time, json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("127.0.0.1", 3452))
sock.sendall(bytes("MAS"+"|", "utf-8"))
input("")
exit()