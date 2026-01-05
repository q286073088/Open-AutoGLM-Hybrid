# Termux 部署问题修复记录

## 已解决的问题

### 1. ❌ pip升级被禁止
**错误信息**:
```
ERROR: Installing pip is forbidden, this will break the python-pip package (termux).
```

**原因**: Termux使用自己的包管理系统，不允许升级pip

**解决方案**: 删除 `pip install --upgrade pip` 命令

---

### 2. ❌ Pillow编译失败
**错误信息**:
```
ERROR: Failed building wheel for pillow
```

**原因**: Pillow需要编译C扩展，缺少图像库依赖

**解决方案**: 安装以下依赖
```bash
pkg install clang libjpeg-turbo libpng zlib freetype -y
```

---

### 3. ❌ openai包编译失败（jiter依赖）
**错误信息**:
```
ERROR: Failed to build 'jiter' when installing build dependencies for jiter
```

**原因**: openai新版本依赖jiter，需要Rust编译器

**解决方案**: 使用旧版本 `openai<1.0.0`（功能完整，无需Rust）
```bash
pip install "openai<1.0.0"
```

---

## 完整部署命令

### 在Termux中执行：

```bash
# 1. 下载最新修复版本的部署脚本
rm deploy.sh
curl -O https://raw.githubusercontent.com/q286073088/Open-AutoGLM-Hybrid/shiys/termux-scripts/deploy.sh

# 2. 赋予执行权限
chmod +x deploy.sh

# 3. 运行部署脚本
./deploy.sh
```

### 脚本会自动完成：

1. ✅ 更新软件包列表
2. ✅ 安装Python和Git
3. ✅ 安装编译工具（clang）
4. ✅ 安装图像库依赖（libjpeg-turbo, libpng, zlib, freetype）
5. ✅ 安装Python依赖（pillow, requests, openai<1.0.0）
6. ✅ 下载并安装Open-AutoGLM
7. ✅ 配置API Key
8. ✅ 创建启动脚本

---

## 预计时间

| 步骤 | 时间 |
|------|------|
| 安装系统依赖 | 5-10分钟 |
| 编译Python包 | 5-10分钟 |
| 下载Open-AutoGLM | 2-5分钟 |
| **总计** | **15-25分钟** |

---

## 需要的存储空间

- Python包: ~150MB
- Open-AutoGLM: ~100MB
- **总计**: ~300MB

---

## 优化说明

### 为什么使用 `openai<1.0.0`？

| 特性 | openai 0.x (旧版) | openai 1.x+ (新版) |
|------|------------------|-------------------|
| **编译需求** | ❌ 不需要 Rust | ✅ 需要 Rust 编译器 |
| **安装时间** | ⚡ 快（~2分钟） | 🐌 慢（~10分钟） |
| **存储空间** | 💾 小（~50MB） | 📦 大（~350MB） |
| **功能** | ✅ 完整支持 | ✅ 完整支持 + 新特性 |
| **API 兼容性** | ✅ 兼容所有OpenAI格式API | ✅ 兼容所有OpenAI格式API |

**结论**: 对于 Open-AutoGLM 项目，0.x 版本功能完全够用，且更适合 Termux 环境。

---

## 故障排除

### 如果仍然遇到编译错误：

1. **检查存储空间**
   ```bash
   df -h
   ```
   确保至少有500MB可用空间

2. **清理缓存**
   ```bash
   pkg clean
   pip cache purge
   ```

3. **重新安装依赖**
   ```bash
   pkg install -y clang libjpeg-turbo libpng zlib freetype
   ```

4. **手动安装Python包**
   ```bash
   export LDFLAGS="-L/data/data/com.termux/files/usr/lib"
   export CFLAGS="-I/data/data/com.termux/files/usr/include"
   pip install pillow --no-cache-dir
   pip install requests --no-cache-dir
   pip install "openai<1.0.0" --no-cache-dir
   ```

---

## 已修复的部署脚本特性

✅ 自动安装所有编译依赖
✅ 设置正确的编译环境变量
✅ 按顺序安装Python包避免冲突
✅ 使用 `--no-cache-dir` 节省空间
✅ 使用 `openai<1.0.0` 避免Rust依赖
✅ 详细的进度提示
✅ 错误处理和提示

---

## 更新日志

- **2026-01-05**: 修复pip升级问题
- **2026-01-05**: 添加Pillow编译依赖
- **2026-01-05**: 优化为使用openai<1.0.0（避免Rust依赖）
- **2026-01-05**: 优化安装顺序和环境变量

---

## 联系方式

如果遇到其他问题，请在GitHub提交Issue：
https://github.com/q286073088/Open-AutoGLM-Hybrid/issues
