#!/data/data/com.termux/files/usr/bin/bash

# Open-AutoGLM 安装修复工具

echo "🔍 检查 Open-AutoGLM 安装状态..."
echo ""

# 检查目录是否存在
if [ ! -d ~/Open-AutoGLM ]; then
    echo "❌ Open-AutoGLM 目录不存在"
    echo "📥 正在下载 Open-AutoGLM..."
    cd ~
    git clone https://github.com/zai-org/Open-AutoGLM.git
    if [ $? -ne 0 ]; then
        echo "❌ 下载失败，请检查网络连接"
        exit 1
    fi
    echo "✅ 下载完成"
else
    echo "✅ Open-AutoGLM 目录存在"
fi

# 检查是否已安装
if python -c "import phone_agent" 2>/dev/null; then
    echo "✅ phone_agent 模块已安装"
else
    echo "❌ phone_agent 模块未安装"
    echo "📦 正在安装 Open-AutoGLM..."
    cd ~/Open-AutoGLM
    pip install -e .
    if [ $? -ne 0 ]; then
        echo "❌ 安装失败"
        exit 1
    fi
    echo "✅ 安装完成"
fi

# 最终测试
echo ""
echo "🧪 测试安装..."
if python -c "import phone_agent; print('✅ phone_agent 模块可用')" 2>/dev/null; then
    echo ""
    echo "🎉 修复完成！现在可以运行："
    echo "  autoglm"
    echo ""
    echo "或者："
    echo "  ~/bin/autoglm"
else
    echo "❌ 安装验证失败，请检查错误信息"
    exit 1
fi
