#!/usr/bin/env python3
"""测试 urllib 访问 HTTP 服务"""

import urllib.request
import json

def test_urllib():
    """测试 urllib.request"""
    print("[测试] urllib.request 访问 /status")
    print("=" * 50)

    try:
        print("1. 创建请求...")
        url = "http://localhost:8080/status"
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Python-urllib/3')

        print("2. 发送请求...")
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"   ✅ 收到响应: HTTP {response.status}")

            print("3. 读取响应体...")
            data = response.read()
            print(f"   ✅ 读取完成: {len(data)} 字节")

            print("4. 解析 JSON...")
            result = json.loads(data.decode('utf-8'))
            print(f"   ✅ JSON 解析成功:")
            print(f"      {json.dumps(result, indent=2, ensure_ascii=False)}")

            if result.get('status') == 'ok':
                print("\n✅ 测试成功！服务正常运行")
                if result.get('accessibility_enabled'):
                    print("✅ 无障碍服务已启用")
                else:
                    print("⚠️  无障碍服务未启用")
                return True
            else:
                print(f"\n⚠️  服务状态异常: {result.get('status')}")
                return False

    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP 错误: {e.code} {e.reason}")
        return False

    except urllib.error.URLError as e:
        print(f"\n❌ URL 错误: {e.reason}")
        return False

    except TimeoutError:
        print("\n❌ 超时！")
        return False

    except Exception as e:
        print(f"\n❌ 错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_urllib()
    exit(0 if success else 1)
