import socket
import threading
import argparse
import os

# Global variables
OK_RESPONSE = "HTTP/1.1 200 OK\r\n\r\n".encode()
NOTFOUND_RESPONSE = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
lock = threading.Lock()  # Lock for synchronization

def handle_client(client_socket, directory):
    while True:
        # Add lock to ensure safe access to shared resources
        with lock:
            try:
                request = client_socket.recv(1024).decode()
                if not request:
                    break

                req = request.split("\r\n")
                url = req[0].split(" ")[1]

                if url == "/":
                    client_socket.sendall(OK_RESPONSE)
                elif url.startswith("/echo"):
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(url[6:])}\r\n\r\n{url[6:]}".encode()
                    client_socket.sendall(response)
                elif url.startswith("/files"):
                    filename = url[len("/files/"):]
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        with open(file_path, "rb") as f:
                            file_content = f.read()
                        response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(file_content)}\r\n\r\n".encode()
                        client_socket.sendall(response + file_content)
                    else:
                        client_socket.sendall(NOTFOUND_RESPONSE)
                elif url.startswith("/user-agent"):
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
            except Exception as e:
                print(f"Exception while handling client: {e}")
                break
    
    client_socket.close()

def main():
    parser = argparse.ArgumentParser(description='Simple HTTP Server')
    parser.add_argument('--directory', required=True, help='Directory where the files are stored')
    args = parser.parse_args()
    directory = args.directory

    try:
        server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
        print("Server started and listening on port 4221")
    except Exception as e:
        print(f"Failed to start server: {e}")
        return

    while True:
        try:
            client_socket, _retaddr = server_socket.accept()
            print("Accepted a new connection")
            client_thread = threading.Thread(target=handle_client, args=(client_socket, directory))
            client_thread.start()
        except Exception as e:
            print(f"Exception while accepting connection: {e}")

if __name__ == "__main__":
    main()
