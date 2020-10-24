#!/usr/bin/env python3

import socket
import sys
import select

from file_reader import FileReader



class Jewel:

    def __init__(self, port, file_path, file_reader):
        self.file_path = file_path
        self.file_reader = file_reader

        import os
        self.port = os.environ['PORT']
        print("port ", port)
        print("environment variables ", os.environ)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(0)
        s.bind(('0.0.0.0', int(self.port)))

        s.listen(5)
        clientAddr = {}
        readable_list = [s]
        writable_list = []
        error_list = []
        writing_queue = {}

        while True:
            ready_to_read, ready_to_write, in_error = select.select(readable_list, writable_list, error_list)
            for readable in ready_to_read:
                if readable == s:
                    (client, address) = s.accept()
                    address = (address[0], self.port)
                    client.setblocking(0)
                    print("[CONN] Connection from ", address[0], " on port ", address[1], flush=True)
                    clientAddr[client] = address
                    readable_list.append(client)
                    writable_list.append(client)
                    writing_queue[client] = []
                else:
                    data = readable.recv(1024)
                    if not data:
                        break
                    else:
                        print("data = ", data)
                        params = str.splitlines(data.decode(encoding='ascii'))
                        requestLine = params[0].split()
                        if requestLine[0] == "GET":
                            print("[REQU] [",clientAddr[readable][0],":",clientAddr[readable][1],"] GET request for",requestLine[1],flush=True)
                            head, body = file_reader.get(file_path+requestLine[1],params[1:len(params)-1])
                            if body != "":
                                writing_queue[readable].append(head+b"\r\n"+body+b"\r\n\r\n")
                            else:
                                writing_queue[readable].append(head)
                        elif requestLine[0] == "HEAD":
                            print("[REQU] [",clientAddr[readable][0],":",clientAddr[readable][1],"] HEAD request for",requestLine[1], flush=True)
                            writing_queue[readable].append(file_reader.head(file_path+requestLine[1],params[1:len(params)-1])+b"\r\n")
                        else:
                            print("[REQU] [",clientAddr[readable][0],":",clientAddr[readable][1],"]",requestLine[0],"request", flush=True)
                            writing_queue[readable].append(b"HTTP/1.1 501 Method Unimplemented\r\n\r\n")
            for writable in ready_to_write:
                if writing_queue[writable]:
                    msg = writing_queue[writable].pop()
                    print("msg is ", msg, flush=True)
                    response_code = str.splitlines(msg[:15].decode(encoding='ascii'))[0].split()[1]
                    if response_code != "200":
                        print("[ERRO] [",clientAddr[writable][0],":",clientAddr[writable][1],"]",requestLine[0],"request returned error",response_code, flush=True)
                    writable.send(msg)
                    if response_code != "200":
                        readable_list.remove(writable)
                        writable_list.remove(writable)
                        writable.close()

if __name__ == "__main__":
    port = int(sys.argv[1])
    file_path = sys.argv[2]

    FR = FileReader()

    J = Jewel(port, file_path, FR)
