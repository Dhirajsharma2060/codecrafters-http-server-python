import socket
import threading
import sys

OK_RESPONSE = "HTTP/1.1 200 OK\r\n\r\n".encode()
NOT_FOUND_RESPONSE = "HTTP/1.1 404 Not Found\r\n\r\n".encode()

class HTTPServer:
    def __init__(self, host, port, directory):
        self.host = host
        self.port = port
        self.directory = directory

    def start(self):
        server_socket = socket.create_server((self.host, self.port), reuse_port=True)
        print(f"Server started and listening on {self.host}:{self.port}")
        while True:
            client_socket, _ = server_socket.accept()
            threading.Thread(target=self.handle_request, args=(client_socket,)).start()

    def handle_request(self, client_socket):
        try:
            request_data = client_socket.recv(1024).decode()
            if not request_data:
                return

            method, path, _ = request_data.split("\r\n")[0].split(" ")
            if method == "GET":
                self.handle_get_request(client_socket, path)
            else:
                client_socket.sendall(NOT_FOUND_RESPONSE)
        except Exception as e:
            print(f"Error handling request: {e}")
        finally:
            client_socket.close()

    def handle_get_request(self, client_socket, path):
        if path == "/":
            response = OK_RESPONSE
        elif path.startswith("/echo"):
            response = self.handle_echo(path)
        elif path.startswith("/user-agent"):
            response = self.handle_user_agent()
        elif path.startswith("/files"):
            response = self.handle_file_request(path[7:])
        else:
            response = NOT_FOUND_RESPONSE

        client_socket.sendall(response)

    def handle_echo(self, path):
        content = path[6:]
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(content)}\r\n\r\n{content}".encode()
        return response

    def handle_user_agent(self):
        user_agent = "Unknown"
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}".encode()
        return response

    def handle_file_request(self, filename):
        try:
            with open(f"{self.directory}/{filename}", "rb") as file:
                content = file.read()
                response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(content)}\r\n\r\n".encode()
                response += content
        except FileNotFoundError:
            response = NOT_FOUND_RESPONSE
        return response

def main():
    if len(sys.argv) != 3:
        print("Usage: python http_server.py <host> <port>")
        return

    host = sys.argv[1]
    port = int(sys.argv[2])
    directory = "/path/to/your/files"  # Specify the directory where your files are stored

    http_server = HTTPServer(host, port, directory)
    http_server.start()

if __name__ == "__main__":
    main()
