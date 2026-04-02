import socket
from contextlib import closing


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


if __name__ == '__main__':
    port = find_free_port()
    print(f"Using port: {port}")
