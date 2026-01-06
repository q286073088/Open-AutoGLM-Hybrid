#!/usr/bin/env python3
"""测试 socket HTTP 实现"""

import socket
import json

def test_socket_http():
    """测试原始 socket HTTP 请求"""
    print("[测试] Socket HTTP GET 请求到 /status")
    print("=" * 50)

    try:
        # 创建连接
        print("1. 创建 socket...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)

        print("2. 连接到 localhost:8080...")
        sock.connect(('127.0.0.1', 8080))
        print("   ✅ 连接成功")

        # 发送 HTTP 请求
        print("3. 发送 HTTP 请求...")
        request = "GET /status HTTP/1.0\r\nHost: localhost\r\nConnection: close\r\n\r\n"
        print(f"   请求内容:\n{repr(request)}")
        sock.sendall(request.encode())
        print("   ✅ 请求已发送")

        # 读取响应
        print("4. 读取响应...")
        response = b""
        chunk_count = 0
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                print(f"   ✅ 读取完成 (共 {chunk_count} 个数据块)")
                break
            chunk_count += 1
            response += chunk
            print(f"   收到数据块 {chunk_count}: {len(chunk)} 字节")

        sock.close()

        # 解析响应
        print("\n5. 解析响应...")
        response_str = response.decode('utf-8', errors='ignore')
        print(f"   原始响应 ({len(response_str)} 字符):")
        print("   " + "-" * 46)
        print("   " + response_str[:500].replace('\n', '\n   '))
        if len(response_str) > 500:
            print(f"   ... (还有 {len(response_str) - 500} 字符)")
        print("   " + "-" * 46)

        # 分离头部和主体
        if '\r\n\r\n' in response_str:
            headers, body = response_str.split('\r\n\r\n', 1)
            print(f"\n   HTTP 头部:")
            for line in headers.split('\r\n'):
                print(f"     {line}")

            print(f"\n   HTTP 主体:")
            print(f"     {body}")

            # 检查状态码
            if '200 OK' in headers or '200' in headers.split('\r\n')[0]:
                print("\n   ✅ 状态码: 200 OK")

                # 尝试解析 JSON
                try:
                    data = json.loads(body)
                    print(f"\n   ✅ JSON 解析成功:")
                    print(f"     {json.dumps(data, indent=2, ensure_ascii=False)}")

                    if data.get('status') == 'ok':
                        print("\n✅ 测试成功！服务正常运行")
                        if data.get('accessibility_enabled'):
                            print("✅ 无障碍服务已启用")
                        else:
                            print("⚠️  无障碍服务未启用")
                    else:
                        print(f"\n⚠️  服务状态异常: {data.get('status')}")

                except json.JSONDecodeError as e:
                    print(f"\n❌ JSON 解析失败: {e}")
                    print(f"   主体内容: {repr(body)}")
            else:
                print(f"\n❌ 状态码错误: {headers.split(chr(13)+chr(10))[0]}")
        else:
            print("\n❌ 响应格式错误: 找不到 HTTP 头部和主体分隔符")

    except socket.timeout:
        print("\n❌ 超时！")
        print("   可能原因:")
        print("   1. 服务端没有响应")
        print("   2. 服务端响应格式不正确")
        print("   3. 连接被阻塞")

    except ConnectionRefusedError:
        print("\n❌ 连接被拒绝！")
        print("   请确保 AutoGLM Helper 正在运行")

    except Exception as e:
        print(f"\n❌ 错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_socket_http()
