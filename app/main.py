import socket

def main():
    print("Logs from your program will appear here!")

    # Create server socket
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    
    while True:
        conn_socket, addr = server_socket.accept()
        with conn_socket:
            data = conn_socket.recv(1024)
            if not data:
                break
            request_line = data.split(b"\r\n")[0]
            request_path = request_line.split(b" ")[1]

            if request_path == b"/":
                response = b"HTTP/1.1 200 OK\r\n\r\n"
            else:
                response = b"HTTP/1.1 404 Not Found\r\n\r\n"
            
            conn_socket.sendall(response)

if __name__ == "__main__":
    main()
