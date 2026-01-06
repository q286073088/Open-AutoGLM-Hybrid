#!/data/data/com.termux/files/usr/bin/bash

# Open-AutoGLM 混合方案 - 完整部署修复工具

echo "🔧 Open-AutoGLM 混合方案 - 完整修复"
echo "=" * 60

# 1. 下载 phone_controller.py
echo "📥 下载 phone_controller.py..."
mkdir -p ~/.autoglm
curl -s -o ~/.autoglm/phone_controller.py https://raw.githubusercontent.com/q286073088/Open-AutoGLM-Hybrid/shiys/termux-scripts/phone_controller.py
if [ $? -eq 0 ]; then
    echo "✅ phone_controller.py 下载完成"
else
    echo "❌ 下载失败"
    exit 1
fi

# 2. 下载主程序
echo "📥 下载主程序..."
curl -s -o ~/.autoglm/autoglm_main.py https://raw.githubusercontent.com/q286073088/Open-AutoGLM-Hybrid/shiys/termux-scripts/autoglm_main.py
if [ $? -eq 0 ]; then
    echo "✅ 主程序下载完成"
else
    echo "❌ 下载失败"
    exit 1
fi

chmod +x ~/.autoglm/autoglm_main.py

# 3. 创建启动脚本
echo "📝 创建启动脚本..."
mkdir -p ~/bin

cat > ~/bin/autoglm << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

# 加载配置
source ~/.autoglm/config.sh

# 启动主程序
python ~/.autoglm/autoglm_main.py
EOF

chmod +x ~/bin/autoglm

# 4. 添加到 PATH
if ! grep -q 'export PATH=$PATH:~/bin' ~/.bashrc; then
    echo 'export PATH=$PATH:~/bin' >> ~/.bashrc
fi

echo ""
echo "✅ 修复完成！"
echo ""
echo "现在可以运行:"
echo "  source ~/.bashrc"
echo "  autoglm"
echo ""
