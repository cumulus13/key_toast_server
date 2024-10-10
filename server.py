import tkinter as tk
from tkinter import ttk
import socket
import threading
import argparse
import sys
from pynput import keyboard

server_running = True

def show_toast(message, duration=3000):
    toast = tk.Toplevel()
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)
    toast.attributes("-alpha", 0.9)
    toast.attributes('-disabled', True)

    screen_width = toast.winfo_screenwidth()
    screen_height = toast.winfo_screenheight()

    width = 200
    height = 50

    x = (screen_width - width) // 2
    y = screen_height - height - 40

    toast.geometry(f"{width}x{height}+{x}+{y}")

    label = ttk.Label(toast, text=message, font=("Arial", 12), background="black", foreground="white", anchor="center")
    label.pack(expand=True, fill='both')

    toast.after(duration, toast.destroy)

def start_server(host='localhost', port=12345):
    global server_running
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    server_socket.settimeout(1)  # Set a timeout for accept() to allow checking server_running flag
    print(f"Server listening on {host}:{port}")
    print("Press 'q' to quit the server.")

    while server_running:
        try:
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")
            
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                print(f"Received message: {data}")
                root.after(0, lambda: show_toast(data))
            
            client_socket.close()
        except socket.timeout:
            continue  # This allows checking the server_running flag periodically
    
    server_socket.close()
    print("Server stopped.")
    
    
def send_message(message, host='localhost', port=12345):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)  # Set a 5-second timeout for the connection attempt
            s.connect((host, port))
            s.sendall(message.encode('utf-8'))
        print(f"Message sent successfully: {message}")
    except ConnectionRefusedError:
        print(f"Error: Could not connect to the server at {host}:{port}. Is the server running?")
    except socket.timeout:
        print(f"Error: Connection to {host}:{port} timed out. The server may be unreachable.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
        
def on_press(key):
    global server_running
    if key == keyboard.KeyCode.from_char('q'):
        print("Quitting server...")
        server_running = False
        root.quit()
        return False  # Stop the listener

def run_server():
    global root
    root = tk.Tk()
    root.withdraw()
    root.attributes('-alpha', 0.0)

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Start listening for the 'q' key press
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    root.mainloop()
    
def main():
    parser = argparse.ArgumentParser(description="Toast Notification Server/Client")
    parser.add_argument("--host", default="localhost", help="Server host (default: localhost)")
    parser.add_argument("--port", type=int, default=12345, help="Server port (default: 12345)")
    parser.add_argument("action", nargs="?", default="server", help="Action to perform: 'server' or 'send'")
    parser.add_argument("message", nargs="*", help="Text to send as a toast notification")

    args = parser.parse_args()

    if args.action == "send":
        if not args.message:
            print("Error: No message provided for 'send' action.")
            parser.print_help()
            sys.exit(1)
        message = " ".join(args.message)
        send_message(message, host=args.host, port=args.port)
    elif args.action == "server":
        run_server()
    else:
        print(f"Error: Unknown action '{args.action}'. Use 'server' or 'send'.")
        parser.print_help()
        sys.exit(1)
        
if __name__ == "__main__":
    main()