#!/data/data/com.termux/files/usr/bin/python
"""
AutoGLM Helper 诊断脚本
用于排查连接问题
"""

import socket
import json
import sys

def http_get(host='localhost', port=8080, path='/status', timeout=30):
    """使用原始 socket 发送 GET 请求"""
    try:
        # 创建 socket 连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        print(f"正在连接 {host}:{port}...")
        sock.connect((host, port))
        print("✅ TCP 连接成功")

        # 构造 HTTP 请求
        request = f"GET {path} HTTP/1.0\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        sock.sendall(request.encode())
        print("✅ HTTP 请求已发送")

        # 读取响应
        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk

        sock.close()
        print("✅ 收到 HTTP 响应")

        # 解析响应
        response_str = response.decode('utf-8', errors='ignore')

        # 分离头部和主体
        if '\r\n\r\n' in response_str:
            headers, body = response_str.split('\r\n\r\n', 1)
        else:
            print("❌ 响应格式错误")
            return None

        print("\n响应头:")
        print("-" * 60)
        for line in headers.split('\r\n'):
            print(f"  {line}")

        print("\n响应体:")
        print("-" * 60)
        print(f"  {body}")

        # 检查状态码
        if '200 OK' not in headers:
            print("\n❌ HTTP 状态码不是 200")
            return None

        print("\n✅ HTTP 状态码: 200 OK")

        # 解析 JSON
        try:
            data = json.loads(body)
            return data
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON 解析失败: {e}")
            return None

    except socket.timeout:
        print(f"❌ 连接超时 ({timeout}秒)")
        print("\n这说明服务器收到了请求但没有及时响应。")
        print("可能的原因:")
        print("1. 你还没有安装最新版本的 APK（包含连接修复）")
        print("2. 服务器处理请求时出现了问题")
        return None
    except ConnectionRefusedError:
        print("❌ 连接被拒绝 - 服务器可能未运行")
        return None
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("=" * 60)
    print("  AutoGLM Helper 诊断工具")
    print("=" * 60)
    print()

    # 步骤 1: 测试 TCP 连接
    print("步骤 1: 测试 TCP 连接")
    print("-" * 60)
    data = http_get()

    if not data:
        print("\n" + "=" * 60)
        print("诊断结果: 无法连接到 AutoGLM Helper")
        print("=" * 60)
        print("\n可能的原因:")
        print("1. AutoGLM Helper APP 未运行")
        print("2. HTTP 服务器未启动")
        print("3. 端口 8080 被其他程序占用")
        print("\n解决方法:")
        print("1. 打开 AutoGLM Helper APP")
        print("2. 检查 APP 界面显示的服务器状态")
        print("3. 尝试在 APP 内点击「测试连接」按钮")
        sys.exit(1)

    # 步骤 2: 检查响应数据
    print("\n步骤 2: 检查响应数据")
    print("-" * 60)

    # 检查 status 字段
    status = data.get('status')
    print(f"status: {status}")
    if status != 'ok':
        print("❌ status 字段不是 'ok'")
    else:
        print("✅ status 字段正确")

    # 检查 service 字段
    service = data.get('service')
    print(f"service: {service}")

    # 检查 version 字段
    version = data.get('version')
    print(f"version: {version}")

    # 检查 build 字段
    build = data.get('build')
    print(f"build: {build}")

    # 检查 accessibility_enabled 字段（关键）
    accessibility_enabled = data.get('accessibility_enabled')
    print(f"accessibility_enabled: {accessibility_enabled}")

    if accessibility_enabled is None:
        print("❌ 缺少 accessibility_enabled 字段")
    elif accessibility_enabled == False:
        print("❌ 无障碍服务未开启")
    else:
        print("✅ 无障碍服务已开启")

    # 步骤 3: 诊断结果
    print("\n" + "=" * 60)
    print("诊断结果")
    print("=" * 60)

    if status == 'ok' and accessibility_enabled == True:
        print("✅ 所有检查通过！AutoGLM Helper 工作正常")
        print("\n如果 autoglm 仍然无法连接，请检查:")
        print("1. 环境变量 AUTOGLM_HELPER_URL 是否正确设置")
        print("2. phone_controller.py 是否在 ~/.autoglm/ 目录下")
        print("3. 运行: python ~/.autoglm/phone_controller.py 测试")
    elif status == 'ok' and accessibility_enabled == False:
        print("❌ AutoGLM Helper 运行中，但无障碍服务未开启")
        print("\n解决方法:")
        print("1. 打开手机「设置」")
        print("2. 进入「无障碍」或「辅助功能」")
        print("3. 找到「AutoGLM Helper」")
        print("4. 开启无障碍服务")
        print("5. 重新运行此诊断脚本")
    else:
        print("❌ AutoGLM Helper 状态异常")
        print("\n解决方法:")
        print("1. 重启 AutoGLM Helper APP")
        print("2. 检查 APP 是否有错误提示")
        print("3. 查看 logcat 日志: logcat | grep AutoGLM")


if __name__ == '__main__':
    main()
