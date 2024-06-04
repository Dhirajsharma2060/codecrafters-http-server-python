import socket
import threading
import argparse  # Added import for argparse

def main():
    def handle_req(client, addr):
        data = client.recv(1024).decode()
        req = data.split("\r\n")
        path = req[0].split(" ")[1]
        if path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n".encode()
        elif path.startswith("/echo"):
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(path[6:])}\r\n\r\n{path[6:]}".encode()
        elif path.startswith("/user-agent"):
            user_agent = req[2].split(": ")[1]
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}".encode()
        elif path.startswith("/files"):
            # Extracted directory argument handling
            directory = args.directory  # Using argparse argument instead of sys.argv[2]
            filename = path[7:]
            try:
                with open(f"{directory}/{filename}", "r") as f:  # Removed leading slash from file path
                    body = f.read()
                response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(body)}\r\n\r\n{body}".encode()
            except Exception as e:
                response = f"HTTP/1.1 404 Not Found\r\n\r\n".encode()
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
        client.send(response)

    # Added argument parser
    parser = argparse.ArgumentParser(description='Simple HTTP Server')
    parser.add_argument('--directory', required=True, help='Directory where the files are stored')
    args = parser.parse_args()

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        client, addr = server_socket.accept()
        threading.Thread(target=handle_req, args=(client, addr)).start()

if __name__ == "__main__":
    main()
