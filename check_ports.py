import socket
import subprocess

ports = [5000, 5175]
for port in ports:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        print(f'port {port} tcp connect_ex ->', result)

try:
    out = subprocess.check_output(['netstat', '-ano'], text=True, stderr=subprocess.STDOUT)
    print('netstat lines for ports:')
    for line in out.splitlines():
        if f':{ports[0]}' in line or f':{ports[1]}' in line:
            print(line)
except Exception as ex:
    print('netstat failed:', ex)
