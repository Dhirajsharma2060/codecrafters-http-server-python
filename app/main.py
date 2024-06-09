import socket
import threading
import sys
import os
import gzip

def main():
    def handle_req(client, addr):
        data = client.recv(1024).decode()
        req = data.split("\r\n")
        method, path, _ = req[0].split(" ")

        if method == "GET":
            handle_get_request(client, path, req, data)
        elif method == "POST" and path.startswith("/files"):
            handle_post_request(client, req, data)
        else:
            response = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n".encode()
            client.send(response)
            client.close()

    def handle_get_request(client, path, req, data):
        headers = {}
        for line in req[1:]:
            if line == '':
                break
            header, value = line.split(": ", 1)
            headers[header.lower()] = value  # Store headers in lowercase for case-insensitive comparison

        accept_encoding = headers.get("accept-encoding", "")  # Get the Accept-Encoding header
        support_gzip = "gzip" in accept_encoding  # Check if gzip is supported

        if path == "/":
            body = "Welcome to the server!".encode()
            content_type = "text/plain"
        elif path.startswith("/echo"):
            body = path[6:].encode()
            content_type = "text/plain"
        elif path.startswith("/user-agent"):
            user_agent = headers.get("user-agent", "")
            body = user_agent.encode()
            content_type = "text/plain"
        elif path.startswith("/files"):
            directory = sys.argv[2]
            filename = path[7:]
            try:
                with open(f"{directory}/{filename}", "rb") as f:
                    body = f.read()
                content_type = "application/octet-stream"  # Correct Content-Type for files
            except Exception as e:
                body = str(e).encode()
                response = f"HTTP/1.1 404 Not Found\r\nContent-Length: {len(body)}\r\n\r\n".encode() + body
                client.send(response)
                client.close()
                return
        else:
            response = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n".encode()
            client.send(response)
            client.close()
            return

        response_headers = [
            "HTTP/1.1 200 OK",
            f"Content-Type: {content_type}",
            f"Content-Length: {len(body)}"
        ]
        
        if support_gzip: # Add Content-Encoding: gzip header if gzip is supported
            compressed_body = gzip.compress(body) 
            response_headers.append("Content-Encoding: gzip")
            body = compressed_body

        response_headers.append("")  # Add an empty line to separate headers from the body

        # Send headers and body separately to handle different types
        response = "\r\n".join(response_headers).encode() + b"\r\n" + body
        client.send(response)
        client.close()

    def handle_post_request(client, req, data):
        headers = {}
        for line in req[1:]:
            if line == '':
                break
            header, value = line.split(": ", 1)
            headers[header.lower()] = value  # Store headers in lowercase for case-insensitive comparison

        content_length = int(headers.get("content-length", 0))
        body_start = data.index("\r\n\r\n") + 4
        file_data = data[body_start:body_start + content_length]
        filename = req[0].split(" ")[1].split("/")[-1]
        directory = sys.argv[2]
        os.makedirs(directory, exist_ok=True)

        try:
            with open(f"{directory}/{filename}", "wb") as f:
                f.write(file_data.encode())
            body = "File uploaded successfully."
            response = f"HTTP/1.1 201 Created\r\nContent-Type: text/plain\r\nContent-Length: {len(body)}\r\n\r\n{body}".encode()
        except Exception as e:
            body = str(e)
            response = f"HTTP/1.1 500 Internal Server Error\r\nContent-Length: {len(body)}\r\n\r\n{body}".encode()

        client.send(response)
        client.close()

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Server started and listening on port 4221")
    while True:
        client, addr = server_socket.accept()
        threading.Thread(target=handle_req, args=(client, addr)).start()

if __name__ == "__main__":
    main()
