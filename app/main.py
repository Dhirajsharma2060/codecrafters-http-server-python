import socket
import re
import threading
import os
import argparse

OK_RESPONSE = "HTTP/1.1 200 OK\r\n\r\n".encode()
NOTFOUND_RESPONSE = "HTTP/1.1 404 Not Found\r\n\r\n".encode()

def handle_client(client_socket, directory):
    while True:
        request = client_socket.recv(1024).decode()
        if not request:
            break  # if no more data, then the connection will break
        
        # Parse the HTTP request
        req = request.split("\r\n")
        url = re.search("GET (.*) HTTP", request).group(1)

        if url == "/":
            client_socket.sendall(OK_RESPONSE)
        elif url.startswith("/echo/"):
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(url[6:])}\r\n\r\n{url[6:]}".encode()
            client_socket.sendall(response)
        elif url.startswith("/files/"):
            # Extract the filename from the URL
            filename = url[len("/files/"):]
            # Construct the full path to the file
            file_path = os.path.join(directory, filename)
            # Check if the file exists and is a file
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, "rb") as f:
                    file_content = f.read()
                # Construct the HTTP response with the file content
                response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(file_content)}\r\n\r\n".encode()
                client_socket.sendall(response + file_content)
            else:
                # Send a 404 response if the file does not exist
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
    
    client_socket.close()

def main():
    parser = argparse.ArgumentParser(description='Simple HTTP Server')
    parser.add_argument('--directory', required=True, help='Directory where the files are stored')
    args = parser.parse_args()
    directory = args.directory

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        client_socket, _retaddr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, directory))
        client_thread.start()

if __name__ == "__main__":
    main()
