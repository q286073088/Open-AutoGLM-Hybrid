#!/data/data/com.termux/files/usr/bin/python
"""
详细诊断 - 找出网络问题
"""

print("=" * 60)
print("详细网络诊断")
print("=" * 60)

# 测试1: socket 直接连接
print("\n[测试1] Socket 直接连接...")
try:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    result = sock.connect_ex(('localhost', 8080))
    if result == 0:
        print("✅ Socket 连接成功")
        sock.close()
    else:
        print(f"❌ Socket 连接失败: {result}")
except Exception as e:
    print(f"❌ 异常: {e}")

# 测试2: 127.0.0.1 vs localhost
print("\n[测试2] 测试 127.0.0.1...")
try:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    result = sock.connect_ex(('127.0.0.1', 8080))
    if result == 0:
        print("✅ 127.0.0.1 连接成功")
        sock.close()
    else:
        print(f"❌ 127.0.0.1 连接失败: {result}")
except Exception as e:
    print(f"❌ 异常: {e}")

# 测试3: http.client 详细测试
print("\n[测试3] http.client 详细测试...")
try:
    from http.client import HTTPConnection
    import json

    print("  创建连接...")
    conn = HTTPConnection('127.0.0.1', 8080, timeout=3)

    print("  发送请求...")
    conn.request("GET", "/status")

    print("  获取响应...")
    response = conn.getresponse()

    print(f"  状态码: {response.status}")
    print(f"  读取数据...")
    data = response.read()
    print(f"  数据长度: {len(data)}")
    print(f"  数据内容: {data[:100]}")

    result = json.loads(data.decode())
    print(f"✅ 成功")
    print(f"  accessibility_enabled: {result.get('accessibility_enabled')}")

    conn.close()
except Exception as e:
    print(f"❌ 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
