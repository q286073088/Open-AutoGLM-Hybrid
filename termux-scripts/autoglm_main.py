#!/data/data/com.termux/files/usr/bin/python
"""
Open-AutoGLM 混合方案 - 主程序
在 Termux 中运行，通过无障碍服务控制手机
"""

import os
import sys
import base64
from io import BytesIO
from openai import OpenAI

# 添加项目路径
sys.path.insert(0, os.path.expanduser('~/.autoglm'))

try:
    from phone_controller import PhoneController
except ImportError:
    print("❌ 错误: 找不到 phone_controller.py")
    print("请确保文件位于 ~/.autoglm/phone_controller.py")
    sys.exit(1)


def image_to_base64(image):
    """将 PIL Image 转换为 base64"""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def main():
    # 读取配置
    api_key = os.getenv('PHONE_AGENT_API_KEY')
    base_url = os.getenv('PHONE_AGENT_BASE_URL', 'https://api.zhongjixun.com/v1')
    model = os.getenv('PHONE_AGENT_MODEL', 'gpt-5-chat-latest')

    if not api_key:
        print("❌ 错误: 未设置 API Key")
        print("请在 ~/.autoglm/config.sh 中设置 PHONE_AGENT_API_KEY")
        sys.exit(1)

    print("=" * 60)
    print("         Open-AutoGLM 混合方案 (Termux)")
    print("=" * 60)
    print(f"API: {base_url}")
    print(f"模型: {model}")
    print("=" * 60)
    print()

    # 初始化控制器
    try:
        controller = PhoneController()
        print(f"✅ 控制模式: {controller.get_mode()}")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        sys.exit(1)

    # 初始化 AI 客户端
    client = OpenAI(api_key=api_key, base_url=base_url)

    print()
    print("使用说明:")
    print("1. 输入任务描述，如: 打开淘宝搜索蓝牙耳机")
    print("2. 输入 'exit' 退出程序")
    print()

    while True:
        try:
            # 获取用户输入
            task = input("请输入任务: ").strip()

            if task.lower() in ['exit', 'quit', 'q']:
                print("再见！")
                break

            if not task:
                continue

            print(f"\n🎯 任务: {task}")
            print("📸 正在截图...")

            # 截图
            screenshot = controller.screenshot()
            if not screenshot:
                print("❌ 截图失败")
                continue

            print(f"✅ 截图成功: {screenshot.size}")

            # 转换为 base64
            image_base64 = image_to_base64(screenshot)

            print("🤖 正在调用 AI 分析...")

            # 调用 AI
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"任务: {task}\n\n请分析当前屏幕，告诉我应该执行什么操作。"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )

            ai_response = response.choices[0].message.content
            print(f"\n🤖 AI 回复:\n{ai_response}\n")

            # 这里可以添加解析 AI 回复并执行操作的逻辑
            # 例如: 解析点击坐标、滑动方向等

        except KeyboardInterrupt:
            print("\n\n👋 用户中断，退出程序")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()
