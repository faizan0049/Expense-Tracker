from app import app  # noqa: F401
import socket

def is_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_free_port(start_port=8080, max_attempts=5):
    """Find a free port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(port):
            return port
    # If no port is found, return a default
    return 8888

if __name__ == "__main__":
    # Try starting with port 8080, but find another if it's in use
    port = find_free_port(8080)
    print(f"Starting application on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
