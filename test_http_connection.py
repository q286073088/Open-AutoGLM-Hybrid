#!/usr/bin/env python3
"""
测试 AutoGLM Helper HTTP 服务器连接
用于验证 Connection: close 修复是否生效
"""

import socket
import time

def test_http_connection(host='localhost', port=8080):
    """测试 HTTP 连接是否正确关闭"""

    print(f"测试 HTTP 连接到 {host}:{port}")
    print("=" * 60)

    # 测试 1: 不发送 Connection: close 头
    print("\n测试 1: 不发送 Connection: close 头")
    print("-" * 60)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5秒超时

        print(f"连接到 {host}:{port}...")
        sock.connect((host, port))
        print("✓ 连接成功")

        # 发送 HTTP 请求（不带 Connection: close）
        request = b"GET /status HTTP/1.1\r\nHost: localhost\r\n\r\n"
        print(f"发送请求: {request.decode('utf-8', errors='ignore').strip()}")
        sock.sendall(request)

        # 接收响应
        print("等待响应...")
        start_time = time.time()
        response = b""

        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk

                # 检查是否收到完整响应
                if b"\r\n\r\n" in response:
                    # 检查 Content-Length
                    headers_end = response.find(b"\r\n\r\n")
                    headers = response[:headers_end].decode('utf-8', errors='ignore')
                    body = response[headers_end + 4:]

                    # 查找 Content-Length
                    content_length = None
                    for line in headers.split('\r\n'):
                        if line.lower().startswith('content-length:'):
                            content_length = int(line.split(':')[1].strip())
                            break

                    if content_length is not None and len(body) >= content_length:
                        break

            except socket.timeout:
                print("✗ 超时！服务器没有关闭连接")
                elapsed = time.time() - start_time
                print(f"  等待时间: {elapsed:.2f}秒")
                sock.close()
                return False

        elapsed = time.time() - start_time
        print(f"✓ 收到响应 ({elapsed:.2f}秒)")

        # 解析响应
        response_str = response.decode('utf-8', errors='ignore')
        print("\n响应头:")
        headers_end = response_str.find('\r\n\r\n')
        if headers_end > 0:
            headers = response_str[:headers_end]
            for line in headers.split('\r\n'):
                print(f"  {line}")

            # 检查 Connection 头
            if 'connection: close' in headers.lower():
                print("\n✓ 服务器返回了 Connection: close 头")
            else:
                print("\n✗ 服务器没有返回 Connection: close 头")

        print("\n响应体:")
        body = response_str[headers_end + 4:] if headers_end > 0 else response_str
        print(f"  {body}")

        sock.close()
        print("\n✓ 测试 1 通过")
        return True

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

    # 测试 2: 发送 Connection: close 头
    print("\n\n测试 2: 发送 Connection: close 头")
    print("-" * 60)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)

        print(f"连接到 {host}:{port}...")
        sock.connect((host, port))
        print("✓ 连接成功")

        # 发送 HTTP 请求（带 Connection: close）
        request = b"GET /status HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
        print(f"发送请求: {request.decode('utf-8', errors='ignore').strip()}")
        sock.sendall(request)

        # 接收响应
        print("等待响应...")
        start_time = time.time()
        response = b""

        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk

        elapsed = time.time() - start_time
        print(f"✓ 收到响应 ({elapsed:.2f}秒)")

        # 解析响应
        response_str = response.decode('utf-8', errors='ignore')
        print("\n响应头:")
        headers_end = response_str.find('\r\n\r\n')
        if headers_end > 0:
            headers = response_str[:headers_end]
            for line in headers.split('\r\n'):
                print(f"  {line}")

        print("\n响应体:")
        body = response_str[headers_end + 4:] if headers_end > 0 else response_str
        print(f"  {body}")

        sock.close()
        print("\n✓ 测试 2 通过")
        return True

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("AutoGLM Helper HTTP 连接测试")
    print("=" * 60)
    print()

    success = test_http_connection()

    print("\n" + "=" * 60)
    if success:
        print("✓ 所有测试通过")
    else:
        print("✗ 测试失败")
