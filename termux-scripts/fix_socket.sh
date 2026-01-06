#!/data/data/com.termux/files/usr/bin/bash

# Open-AutoGLM 混合方案 - Socket 修复更新

echo "🔧 更新 phone_controller.py (Socket 修复版本)"
echo "================================================"

# 下载更新后的 phone_controller.py
echo "📥 下载更新..."
curl -s -o ~/.autoglm/phone_controller.py https://raw.githubusercontent.com/q286073088/Open-AutoGLM-Hybrid/shiys/termux-scripts/phone_controller.py

if [ $? -eq 0 ]; then
    echo "✅ 更新完成！"
    echo ""
    echo "修复内容:"
    echo "  - 使用原始 socket 替代 http.client"
    echo "  - 解决 Termux 中 getresponse() 超时问题"
    echo "  - 使用 HTTP/1.0 协议确保兼容性"
    echo ""
    echo "现在可以运行: autoglm"
else
    echo "❌ 下载失败，请检查网络连接"
    exit 1
fi
