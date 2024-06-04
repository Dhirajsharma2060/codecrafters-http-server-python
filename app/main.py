import socket
import re
import threading
import os
import argparse

# Define HTTP response codes
OK_RESPONSE = "HTTP/1.1 200 OK\r\n\r\n".encode()
NOTFOUND_RESPONSE = "HTTP/1.1 404 Not Found\r\n\r\n".encode()

def handle_client(client_socket, directory):
    while True:
        try:
            # Receive and decode client request
            request = client_socket.recv(1024).decode()
            if not request:
                break  # If no more data, break the connection

            # Parse the HTTP request
            req = request.split("\r\n")
            url = re.search("GET (.*) HTTP", request).group(1)

            if url == "/":
                # Send OK response for the root path
                client_socket.sendall(OK_RESPONSE)
            elif url.startswith("/echo/"):
                # Send back the echo response
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(url[6:])}\r\n\r\n{url[6:]}".encode()
                client_socket.sendall(response)
            elif url.startswith("/files/"):
                # Extract the filename from the URL
                filename = url[len("/files/"):]
                # Construct the full path to the file
                file_path = os.path.join(directory, filename)
                # Check if the file exists and is a regular file
                if os.path.isfile(file_path):
                    with open(file_path, "rb") as f:
                        file_content = f.read()
                    # Send the file content as the HTTP response
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(file_content)}\r\n\r\n".encode()
                    client_socket.sendall(response + file_content)
                else:
                    # Send 404 response if the file doesn't exist
                    client_socket.sendall(NOTFOUND_RESPONSE)
            elif url.startswith("/user-agent"):
                # Extract User-Agent header from request
                user_agent = ""
                for header in req:
                    if header.startswith("User-Agent:"):
                        user_agent = header.split(": ")[1]
                        break
                # Send User-Agent in the response
                if user_agent:
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}".encode()
                    client_socket.sendall(response)
                else:
                    # Send 404 response if User-Agent header is missing
                    client_socket.sendall(NOTFOUND_RESPONSE)
            else:
                # Send 404 response for unknown paths
                client_socket.sendall(NOTFOUND_RESPONSE)
        
        except Exception as e:
            # Handle exceptions and close the connection
            print(f"Exception while handling client: {e}")
            break
    
    # Close the client socket
    client_socket.close()

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Simple HTTP Server')
    parser.add_argument('--directory', required=True, help='Directory where the files are stored')
    args = parser.parse_args()
    directory = args.directory

    try:
        # Create a server socket
        server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
        print("Server started and listening on port 4221")
    except Exception as e:
        # Handle server creation failure
        print(f"Failed to start server: {e}")
        return

    while True:
        try:
            # Accept incoming client connections
            client_socket, _retaddr = server_socket.accept()
            print("Accepted a new connection")
            # Create a new thread to handle each client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, directory))
            client_thread.start()
        except Exception as e:
            # Handle client connection failure
            print(f"Exception while accepting connection: {e}")

if __name__ == "__main__":
    main()
