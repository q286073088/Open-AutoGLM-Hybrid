#!/data/data/com.termux/files/usr/bin/python
"""
实时查看 AutoGLM 日志
"""

import subprocess
import sys

def main():
    print("开始监控 AutoGLM 日志...")
    print("按 Ctrl+C 停止")
    print("=" * 60)

    try:
        # 清空现有日志
        subprocess.run(["logcat", "-c"], check=False)

        # 实时显示日志
        process = subprocess.Popen(
            ["logcat", "-s", "AutoGLM-SimpleHttpServer:*", "AutoGLM-Service:*"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        for line in process.stdout:
            print(line.rstrip())

    except KeyboardInterrupt:
        print("\n\n停止监控")
        process.kill()
    except Exception as e:
        print(f"错误: {e}")

if __name__ == '__main__':
    main()
