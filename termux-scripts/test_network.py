#!/data/data/com.termux/files/usr/bin/python
"""
简单测试脚本 - 诊断网络问题
"""

import subprocess
import json

print("=" * 60)
print("网络诊断测试")
print("=" * 60)

# 测试1: 系统 curl
print("\n[测试1] 系统 curl 命令...")
result = subprocess.run(['curl', '-s', 'http://localhost:8080/status'],
                       capture_output=True, text=True, timeout=5)
print(f"返回码: {result.returncode}")
if result.returncode == 0:
    print(f"✅ 成功")
    print(f"输出: {result.stdout[:100]}")
else:
    print(f"❌ 失败")

# 测试2: Python subprocess + curl
print("\n[测试2] Python subprocess + curl...")
try:
    result = subprocess.run(
        ['curl', '-s', '-m', '3', 'http://localhost:8080/status'],
        capture_output=True,
        text=True,
        timeout=4
    )
    if result.returncode == 0 and result.stdout:
        data = json.loads(result.stdout)
        print(f"✅ 成功")
        print(f"accessibility_enabled: {data.get('accessibility_enabled')}")
    else:
        print(f"❌ 失败: 返回码 {result.returncode}")
except Exception as e:
    print(f"❌ 异常: {e}")

# 测试3: Python urllib
print("\n[测试3] Python urllib...")
try:
    from urllib.request import urlopen
    from urllib.error import URLError
    import socket

    # 设置超时
    socket.setdefaulttimeout(3)

    response = urlopen('http://localhost:8080/status')
    data = json.loads(response.read().decode())
    print(f"✅ 成功")
    print(f"accessibility_enabled: {data.get('accessibility_enabled')}")
except Exception as e:
    print(f"❌ 失败: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
