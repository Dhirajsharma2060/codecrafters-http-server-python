import socket
import re
OK_RESPONSE = "HTTP/1.1 200 OK\r\n\r\n".encode()
NOTFOUND_RESPONSE = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")
    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client_socket, _retaddr = server_socket.accept()
    request = client_socket.recv(1024).decode()
    req = request.split("\r\n")
    url = re.search("GET (.*) HTTP", request).group(1)
    while True:

        if not request:
                break  # if no more data, then the connection will break
        elif url == "/":
            client_socket.sendall(OK_RESPONSE)
        elif url.startswith("/echo/"):
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(url[6:])}\r\n\r\n{url[6:]}".encode()
            client_socket.sendall(response)
        elif url.startswith("/user-agent"):
            user_agent = req[2].split(": ")[1]
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}".encode()    
        else:
            client_socket.sendall(NOTFOUND_RESPONSE)
if __name__ == "__main__":
    main()

