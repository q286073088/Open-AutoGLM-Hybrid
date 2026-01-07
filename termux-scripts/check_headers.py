#!/data/data/com.termux/files/usr/bin/python
"""
检查 HTTP 响应头
"""

import socket

def check_response_headers():
    """检查响应头中是否包含 Connection: close"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('localhost', 8080))

        # 发送 HTTP/1.1 请求（不带 Connection: close）
        request = b"GET /status HTTP/1.1\r\nHost: localhost\r\n\r\n"
        sock.sendall(request)

        # 只读取响应头
        response = b""
        while b"\r\n\r\n" not in response:
            chunk = sock.recv(1024)
            if not chunk:
                break
            response += chunk

        sock.close()

        # 解析响应头
        response_str = response.decode('utf-8', errors='ignore')
        headers_end = response_str.find('\r\n\r\n')
        if headers_end > 0:
            headers = response_str[:headers_end]
            print("响应头:")
            print("=" * 60)
            for line in headers.split('\r\n'):
                print(line)
            print("=" * 60)

            # 检查 Connection 头
            if 'connection: close' in headers.lower():
                print("\n✅ 响应头包含 Connection: close")
            else:
                print("\n❌ 响应头不包含 Connection: close")

            # 检查 HTTP 版本
            first_line = headers.split('\r\n')[0]
            if 'HTTP/1.0' in first_line:
                print("✅ HTTP 版本: 1.0")
            elif 'HTTP/1.1' in first_line:
                print("⚠️  HTTP 版本: 1.1 (可能导致持久连接)")

    except Exception as e:
        print(f"错误: {e}")

if __name__ == '__main__':
    check_response_headers()
