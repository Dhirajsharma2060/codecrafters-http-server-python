import socket
import threading
import sys

def main():
    def handle_req(client, addr):
        data = client.recv(1024).decode()
        req = data.split("\r\n")
        method, path, _ = req[0].split(" ")
        
        if method == "GET":
            handle_get_request(client, path)
        elif method == "POST" and path.startswith("/files"):
            handle_post_request(client, req)
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
            client.send(response)
            client.close()

    def handle_get_request(client, path):
        if path == "/":
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nWelcome to the server!".encode()
        elif path.startswith("/echo"):
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n{path[6:]}".encode()
        elif path.startswith("/user-agent"):
            user_agent = client.recv(1024).decode()
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n{user_agent}".encode()
        elif path.startswith("/files"):
            directory = sys.argv[2]
            filename = path[7:]
            try:
                with open(f"/{directory}/{filename}", "r") as f:
                    body = f.read()
                response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(body)}\r\n\r\n{body}".encode()
            except Exception as e:
                response = f"HTTP/1.1 404 Not Found\r\n\r\n{e}".encode()
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
        client.send(response)
        client.close()

    def handle_post_request(client, req):
        # Extract the file content from the request body
        file_data = req[-1]
        # Extract the filename from the request path
        filename = req[0].split(" ")[1].split("/")[-1]
        # Specify the directory where files will be saved
        directory = sys.argv[2]
        try:
            with open(f"/{directory}/{filename}", "wb") as f:
                f.write(file_data.encode())
            response = "HTTP/1.1 201 Created\r\nContent-Type: text/plain\r\n\r\nFile uploaded successfully.".encode()
        except Exception as e:
            response = f"HTTP/1.1 500 Internal Server Error\r\n\r\n{e}".encode()
        client.send(response)
        client.close()

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Server started and listening on port 4221")
    while True:
        client, addr = server_socket.accept()
        threading.Thread(target=handle_req, args=(client, addr)).start()

if __name__ == "__main__":
    main()
