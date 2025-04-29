import socket
import json
import argparse
import time

# Client configuration
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

def send_render_request(room_name, step_number, ground_truth):
    """Send a rendering request to the Blender server"""
    start_time = time.time()
    
    # Prepare the request data
    request_data = {
        'room_name': room_name,
        'step_number': step_number,
        'ground_truth': ground_truth
    }
    
    # Convert to JSON
    json_data = json.dumps(request_data)
    
    try:
        # Connect to the server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(json_data.encode('utf-8'))
            
            # Get the response
            response = s.recv(4096).decode('utf-8')
            
        end_time = time.time()
        print(f"Response from server: {response}")
        print(f"Request completed in {end_time - start_time:.2f} seconds")
        
    except ConnectionRefusedError:
        print("Error: Could not connect to the Blender server. Make sure it's running.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send rendering requests to the Blender server")
    parser.add_argument("--room_name", type=str, required=True, help="Room name to process")
    parser.add_argument("--step_number", type=int, default=1, help="Step number to process")
    parser.add_argument("--ground_truth", type=str, default="false", help="Use ground truth (true/false)")
    
    args = parser.parse_args()
    send_render_request(args.room_name, args.step_number, args.ground_truth == "true")