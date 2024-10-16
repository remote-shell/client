import socket
import os

# ANSI escape codes for colored text
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

# File transfer buffer size
BUFFER_SIZE = 4096

def upload_file(client, filename):
    """Handles file upload to the server."""
    try:
        with open(filename, 'rb') as file:
            client.sendall(file.read())
        print(f"{GREEN}File '{filename}' uploaded successfully.{RESET}")
    except FileNotFoundError:
        print(f"{RED}File '{filename}' not found.{RESET}")
    except Exception as e:
        print(f"{RED}Error during file upload: {e}{RESET}")

def download_file(client, filename):
    """Handles file download from the server."""
    try:
        with open(filename, 'wb') as file:
            while True:
                data = client.recv(BUFFER_SIZE)
                if not data:
                    break
                file.write(data)
        print(f"{GREEN}File '{filename}' downloaded successfully.{RESET}")
    except Exception as e:
        print(f"{RED}Error during file download: {e}{RESET}")

def handle_command(client, command):
    """Handles sending a command to the server and processing the response."""
    client.send(command.encode('utf-8'))

    if command.startswith("upload"):
        filename = command.split(" ")[1]
        upload_file(client, filename)
    elif command.startswith("download"):
        filename = command.split(" ")[1]
        download_file(client, filename)
    else:
        response = client.recv(BUFFER_SIZE).decode('utf-8')
        print(f"{GREEN}{response}{RESET}")

def request_auth_method(client):
    """Ask the server for the authentication method."""
    client.send(b'auth_method')
    auth_method = client.recv(BUFFER_SIZE).decode('utf-8')
    print(f"Authentication method: {auth_method}")
    return auth_method

def authenticate(client, auth_method):
    """Handles authentication based on the server's method."""
    if auth_method == 'nujc':  # No user account needed
        print(f"{GREEN}No user account required. Proceeding...{RESET}")
        return True
    elif auth_method == 'uac-p':  # User account and password required
        username = input("Username: ").strip()
        client.send(username.encode('utf-8'))

        password = input("Password: ").strip()
        client.send(password.encode('utf-8'))

        # Receive authentication response
        auth_response = client.recv(BUFFER_SIZE).decode('utf-8')
        if 'Authenticated' in auth_response:
            print(f"{GREEN}{auth_response}{RESET}")
            return True
        else:
            print(f"{RED}{auth_response}{RESET}")
            return False
    else:
        print(f"{RED}Unknown authentication method: {auth_method}{RESET}")
        return False

def start_client(domain, port):
    """Main client logic that handles connection, authentication, and command execution."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((domain, port))
        print(f"Connected to rmsh server at {domain}:{port}")

        # Get authentication method from the server
        auth_method = request_auth_method(client)

        # Perform authentication
        if not authenticate(client, auth_method):
            print(f"{RED}Authentication failed. Exiting...{RESET}")
            client.close()
            return

        # Command execution loop
        while True:
            command = input("rmsh> ").strip()

            if command == 'exit':
                print("Exiting rmsh...")
                client.send(command.encode('utf-8'))
                break

            handle_command(client, command)

    except socket.error as e:
        print(f"{RED}Error: {e}{RESET}")
    finally:
        client.close()
        print("Connection closed.")

if __name__ == '__main__':
    domain = input("Enter server domain (or IP): ").strip()
    port = int(input("Enter server port: ").strip())
    start_client(domain, port)