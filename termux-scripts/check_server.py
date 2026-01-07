#!/data/data/com.termux/files/usr/bin/python
"""
检查 HTTP 服务器状态
"""

import subprocess
import time

def check_server_running():
    """检查服务器是否在运行"""
    print("检查 HTTP 服务器状态...")
    print("=" * 60)

    # 1. 检查端口是否被监听
    print("\n1. 检查端口 8080 是否被监听:")
    try:
        result = subprocess.run(
            ["netstat", "-tuln"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "8080" in result.stdout:
            print("✅ 端口 8080 正在被监听")
            for line in result.stdout.split('\n'):
                if "8080" in line:
                    print(f"   {line}")
        else:
            print("❌ 端口 8080 没有被监听")
            print("   服务器可能没有启动！")
    except Exception as e:
        print(f"❌ 无法检查端口: {e}")

    # 2. 检查 AutoGLM 进程
    print("\n2. 检查 AutoGLM 进程:")
    try:
        result = subprocess.run(
            ["ps", "-A"],
            capture_output=True,
            text=True,
            timeout=5
        )
        found = False
        for line in result.stdout.split('\n'):
            if "autoglm" in line.lower() or "helper" in line.lower():
                print(f"   {line}")
                found = True
        if not found:
            print("❌ 没有找到 AutoGLM 相关进程")
    except Exception as e:
        print(f"❌ 无法检查进程: {e}")

    # 3. 检查最近的日志
    print("\n3. 检查最近的日志:")
    try:
        result = subprocess.run(
            ["logcat", "-d", "-s", "AutoGLM-SimpleHttpServer:*", "AutoGLM-Service:*", "AutoGLM-HttpServer:*"],
            capture_output=True,
            text=True,
            timeout=5
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) > 0 and lines[0]:
            print("   最近的日志:")
            for line in lines[-20:]:  # 显示最后 20 行
                if line.strip():
                    print(f"   {line}")
        else:
            print("❌ 没有找到任何日志")
            print("   这说明服务器可能没有启动，或者日志被清空了")
    except Exception as e:
        print(f"❌ 无法读取日志: {e}")

    # 4. 尝试连接
    print("\n4. 尝试 TCP 连接:")
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 8080))
        if result == 0:
            print("✅ TCP 连接成功")
            sock.close()
        else:
            print(f"❌ TCP 连接失败，错误码: {result}")
    except Exception as e:
        print(f"❌ TCP 连接失败: {e}")

    print("\n" + "=" * 60)
    print("诊断建议:")
    print("1. 如果端口没有被监听，说明服务器没有启动")
    print("   - 打开 AutoGLM Helper APP")
    print("   - 检查 APP 是否显示「服务器运行中」")
    print("   - 尝试重启 APP")
    print("\n2. 如果端口被监听但没有日志，说明:")
    print("   - 可能是旧的 HttpServer (NanoHTTPD) 还在运行")
    print("   - 需要完全重启无障碍服务")
    print("   - 方法: 设置 -> 无障碍 -> 关闭 AutoGLM Helper -> 重新开启")
    print("\n3. 如果有日志但请求没有到达，说明:")
    print("   - 可能是网络问题")
    print("   - 尝试使用 127.0.0.1 而不是 localhost")

if __name__ == '__main__':
    check_server_running()
