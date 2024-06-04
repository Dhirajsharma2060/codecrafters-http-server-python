import socket
import re
import threading

OK_RESPONSE = "HTTP/1.1 200 OK\r\n\r\n".encode()
NOTFOUND_RESPONSE = "HTTP/1.1 404 Not Found\r\n\r\n".encode()

def handle_client(client_socket):
    while True:
        request = client_socket.recv(1024).decode()
        if not request:
            break  # if no more data, then the connection will break
        req = request.split("\r\n")
        url = re.search("GET (.*) HTTP", request).group(1)
        
        if url == "/":
            client_socket.sendall(OK_RESPONSE)
        elif url.startswith("/echo/"):
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(url[6:])}\r\n\r\n{url[6:]}".encode()
            client_socket.sendall(response)
        elif url.startswith("/user-agent"):
            # Find the User-Agent header
            user_agent = ""
            for header in req:
                if header.startswith("User-Agent:"):
                    user_agent = header.split(": ")[1]
                    break
            if user_agent:
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}".encode()
                client_socket.sendall(response)
            else:
                client_socket.sendall(NOTFOUND_RESPONSE)
        else:
            client_socket.sendall(NOTFOUND_RESPONSE)
    
    client_socket.close()

def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        client_socket, _retaddr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    main()
