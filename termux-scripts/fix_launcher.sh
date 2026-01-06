#!/data/data/com.termux/files/usr/bin/bash

# Open-AutoGLM 启动脚本修复工具
# 用于修复部署脚本中启动命令创建失败的问题

echo "正在修复启动脚本..."

# 创建 ~/bin 目录
mkdir -p ~/bin

# 创建启动脚本
cat > ~/bin/autoglm << 'LAUNCHER_EOF'
#!/data/data/com.termux/files/usr/bin/bash

# 加载配置
source ~/.autoglm/config.sh

# 启动 AutoGLM
cd ~/Open-AutoGLM
python -m phone_agent.cli
LAUNCHER_EOF

# 赋予执行权限
chmod +x ~/bin/autoglm

# 添加到 PATH
if ! grep -q 'export PATH=$PATH:~/bin' ~/.bashrc; then
    echo 'export PATH=$PATH:~/bin' >> ~/.bashrc
fi

echo "✅ 修复完成！"
echo ""
echo "现在可以使用以下命令启动："
echo "  source ~/.bashrc"
echo "  autoglm"
echo ""
echo "或者直接运行："
echo "  ~/bin/autoglm"
