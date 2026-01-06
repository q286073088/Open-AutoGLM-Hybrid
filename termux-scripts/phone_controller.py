"""
Open-AutoGLM 混合方案 - 手机控制器（使用原始 socket）
版本: 1.0.3

使用原始 socket 实现 HTTP 请求，解决 Termux 中 http.client 兼容性问题
"""

import json
import base64
import logging
import socket
from typing import Optional
from PIL import Image
from io import BytesIO
from urllib.parse import urlparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PhoneController')


def http_get(url: str, timeout: int = 3) -> Optional[dict]:
    """使用原始 socket 发送 GET 请求"""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or 'localhost'
        port = parsed.port or 8080
        path = parsed.path or "/"

        # 创建 socket 连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))

        # 构造 HTTP 请求
        request = f"GET {path} HTTP/1.0\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        sock.sendall(request.encode())

        # 读取响应
        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk

        sock.close()

        # 解析响应
        response_str = response.decode('utf-8', errors='ignore')

        # 分离头部和主体
        if '\r\n\r\n' in response_str:
            headers, body = response_str.split('\r\n\r\n', 1)
        else:
            return None

        # 检查状态码
        if '200 OK' not in headers:
            return None

        # 解析 JSON
        return json.loads(body)

    except Exception as e:
        logger.debug(f"HTTP GET 失败: {e}")
        return None


def http_post(url: str, data: dict, timeout: int = 5) -> Optional[dict]:
    """使用原始 socket 发送 POST 请求"""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or 'localhost'
        port = parsed.port or 8080
        path = parsed.path or "/"

        # 准备请求体
        body = json.dumps(data)
        body_bytes = body.encode('utf-8')

        # 创建 socket 连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))

        # 构造 HTTP 请求
        request = (
            f"POST {path} HTTP/1.0\r\n"
            f"Host: {host}\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {len(body_bytes)}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        )
        sock.sendall(request.encode() + body_bytes)

        # 读取响应
        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk

        sock.close()

        # 解析响应
        response_str = response.decode('utf-8', errors='ignore')

        # 分离头部和主体
        if '\r\n\r\n' in response_str:
            headers, body = response_str.split('\r\n\r\n', 1)
        else:
            return None

        # 检查状态码
        if '200 OK' not in headers:
            return None

        # 解析 JSON
        return json.loads(body)

    except Exception as e:
        logger.debug(f"HTTP POST 失败: {e}")
        return None


class PhoneController:
    """手机控制器 - 支持自动降级"""

    MODE_ACCESSIBILITY = "accessibility"
    MODE_NONE = "none"

    def __init__(self, helper_url: str = "http://localhost:8080"):
        self.helper_url = helper_url
        self.mode = self.MODE_NONE
        self._detect_mode()

    def _detect_mode(self):
        """检测可用的控制模式"""
        logger.info("检测可用的控制模式...")

        if self._try_accessibility_service():
            self.mode = self.MODE_ACCESSIBILITY
            logger.info(f"✅ 使用无障碍服务模式 ({self.helper_url})")
            return

        self.mode = self.MODE_NONE
        logger.error("❌ 无可用控制方式")
        raise Exception(
            "无法连接到手机控制服务！\n"
            "请确保:\n"
            "1. AutoGLM Helper 已运行并开启无障碍权限\n"
        )

    def _try_accessibility_service(self) -> bool:
        """尝试连接无障碍服务"""
        try:
            data = http_get(f"{self.helper_url}/status", timeout=3)

            if data and data.get('status') == 'ok':
                if data.get('accessibility_enabled'):
                    return True
                else:
                    logger.warning("AutoGLM Helper 运行中，但无障碍服务未开启")
                    return False

            return False
        except Exception as e:
            logger.debug(f"无障碍服务连接失败: {e}")
            return False

    def get_mode(self) -> str:
        return self.mode

    def screenshot(self) -> Optional[Image.Image]:
        """截取屏幕"""
        if self.mode == self.MODE_ACCESSIBILITY:
            return self._screenshot_accessibility()
        else:
            logger.error("无可用的截图方式")
            return None

    def _screenshot_accessibility(self) -> Optional[Image.Image]:
        """通过无障碍服务截图"""
        try:
            data = http_get(f"{self.helper_url}/screenshot", timeout=10)

            if data and data.get('success'):
                image_data = base64.b64decode(data['image'])
                image = Image.open(BytesIO(image_data))
                logger.debug(f"截图成功: {image.size}")
                return image

            logger.error("截图失败")
            return None

        except Exception as e:
            logger.error(f"截图失败: {e}")
            return None

    def tap(self, x: int, y: int) -> bool:
        """执行点击操作"""
        if self.mode == self.MODE_ACCESSIBILITY:
            return self._tap_accessibility(x, y)
        else:
            logger.error("无可用的点击方式")
            return False

    def _tap_accessibility(self, x: int, y: int) -> bool:
        """通过无障碍服务点击"""
        try:
            data = http_post(
                f"{self.helper_url}/tap",
                {'x': x, 'y': y},
                timeout=5
            )

            if data:
                success = data.get('success', False)
                logger.debug(f"点击 ({x}, {y}): {success}")
                return success

            return False

        except Exception as e:
            logger.error(f"点击失败: {e}")
            return False

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """执行滑动操作"""
        if self.mode == self.MODE_ACCESSIBILITY:
            return self._swipe_accessibility(x1, y1, x2, y2, duration)
        else:
            logger.error("无可用的滑动方式")
            return False

    def _swipe_accessibility(self, x1: int, y1: int, x2: int, y2: int, duration: int) -> bool:
        """通过无障碍服务滑动"""
        try:
            data = http_post(
                f"{self.helper_url}/swipe",
                {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'duration': duration},
                timeout=10
            )

            if data:
                success = data.get('success', False)
                logger.debug(f"滑动 ({x1},{y1}) -> ({x2},{y2}): {success}")
                return success

            return False

        except Exception as e:
            logger.error(f"滑动失败: {e}")
            return False

    def input_text(self, text: str) -> bool:
        """输入文字"""
        if self.mode == self.MODE_ACCESSIBILITY:
            return self._input_accessibility(text)
        else:
            logger.error("无可用的输入方式")
            return False

    def _input_accessibility(self, text: str) -> bool:
        """通过无障碍服务输入"""
        try:
            data = http_post(
                f"{self.helper_url}/input",
                {'text': text},
                timeout=5
            )

            if data:
                success = data.get('success', False)
                logger.debug(f"输入文字: {success}")
                return success

            return False

        except Exception as e:
            logger.error(f"输入失败: {e}")
            return False


# 测试代码
if __name__ == '__main__':
    print("测试 PhoneController...")

    try:
        controller = PhoneController()
        print(f"当前模式: {controller.get_mode()}")

        print("测试截图...")
        img = controller.screenshot()
        if img:
            print(f"截图成功: {img.size}")
        else:
            print("截图失败")

    except Exception as e:
        print(f"错误: {e}")
