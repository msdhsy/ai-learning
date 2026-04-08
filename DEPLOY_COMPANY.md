# 公司电脑部署指南 - OpenClaw + AI 学习助手

**创建时间**: 2026-04-08 23:50
**用途**: 在公司电脑复刻 OpenClaw 学习环境，利用空闲时间继续学习

---

## 📋 部署清单

### 前置条件
- [ ] Node.js v18+ 已安装
- [ ] npm 可用
- [ ] 公司网络允许访问外部 API（或已配置代理）
- [ ] AI 模型 API 密钥（阿里云百炼/OpenAI/Claude 等）

### 步骤 1: 安装 Node.js（如未安装）
```bash
# 下载地址：https://nodejs.org/
# 选择 LTS 版本（v20+ 推荐）
# 安装后验证：
node -v
npm -v
```

### 步骤 2: 安装 OpenClaw
```bash
npm install -g openclaw
openclaw gateway start
openclaw gateway status
```

### 步骤 3: 克隆学习仓库
```bash
# 选择工作目录
cd D:\work  # 或你喜欢的目录

# 克隆仓库
git clone https://github.com/msdhsy/ai-learning.git
cd ai-learning
```

### 步骤 4: 配置 OpenClaw
```bash
# 初始化配置
openclaw config

# 或手动编辑配置文件（路径根据系统不同）：
# Windows: %USERPROFILE%\.openclaw\config.json
```

**关键配置项**：
```json
{
  "model": "bailian/qwen3.5-plus",
  "timezone": "Asia/Shanghai",
  "shell": "powershell"
}
```

### 步骤 5: 配置 AI 模型 API 密钥
⚠️ **重要**: API 密钥不要提交到 Git！

**方式 A: 环境变量（推荐）**
```bash
# PowerShell
$env:DASHSCOPE_API_KEY="你的密钥"

# 或写入 .env 文件（已在.gitignore 中）
echo "DASHSCOPE_API_KEY=你的密钥" > .env
```

**方式 B: OpenClaw 配置**
```bash
openclaw config set model.apiKey "你的密钥"
```

### 步骤 6: 验证部署
```bash
# 检查 OpenClaw 状态
openclaw gateway status

# 测试对话
# 通过 Web UI 或命令行发送消息
```

---

## 📁 需要同步的文件

### ✅ 可以提交到 Git 的
```
workspace/
├── AGENTS.md          # 代理行为指南
├── SOUL.md            # 人格定义
├── USER.md            # 用户信息
├── IDENTITY.md        # 身份定义
├── MEMORY.md          # 长期记忆（不含敏感信息）
├── HEARTBEAT.md       # 心跳任务（通常为空）
├── TOOLS.md           # 工具配置（不含密码）
├── DEPLOY_COMPANY.md  # 本文件
├── memory/            # 每日学习记录
│   ├── 2026-04-06.md
│   └── 2026-04-07.md
└── py/                # 练习代码
    ├── *.py
    └── .gitignore
```

### ❌ 不要提交到 Git 的
```
- .env                 # API 密钥
- config.json          # 可能含敏感配置
- *.log                # 日志文件
- __pycache__/         # Python 缓存
- *.pyc                # Python 编译文件
```

---

## 🔧 公司网络问题处理

### 如果公司网络限制 GitHub
```bash
# 配置 Git 代理（和你家电脑一样）
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 或使用 SSH（如果公司允许）
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

### 如果公司网络限制 AI API
- 使用手机热点
- 或申请公司代理
- 或换用国内模型（阿里云百炼、智谱等）

---

## 🚀 部署后第一天使用

1. **启动 OpenClaw**
   ```bash
   openclaw gateway start
   ```

2. **访问 Web UI**
   - 浏览器打开：http://localhost:8080（或配置的端口）

3. **继续学习**
   - Day 3: FastAPI 入门
   - 把 chatbot 改成 Web API

---

## ⚠️ 常见问题

| 问题 | 解决方案 |
|------|----------|
| `openclaw: command not found` | npm 全局安装路径未加入 PATH，重启终端或手动添加 |
| 端口被占用 | 修改配置文件中的端口，或关闭占用程序 |
| API 密钥无效 | 检查密钥是否正确，是否有余额 |
| 网络连接超时 | 配置代理或使用热点 |

---

## 📞 需要帮助？

部署遇到问题，在家里 OpenClaw 问我，我会帮你解决。

---

**最后提醒**: 
- API 密钥单独保存，不要提交 Git
- 公司电脑和家里电脑是两个独立实例，记忆不会自动同步
- 建议每天学习结束后，把 `memory/` 文件 commit 推送到 GitHub，这样两边记忆可以手动同步

```bash
# 每天学习结束后
git add memory/
git commit -m "Day X: 学习内容摘要"
git push

# 公司电脑拉取
git pull
```
