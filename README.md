# 📈 美股新闻监控机器人 — 部署指南

**全程免费，不用开一直开着电脑**

---

## 你需要准备的东西

1. **GitHub 账号** ✅（你已有）
2. **Google 账号** ✅（你已有）→ 用来获取 Gemini API Key
3. **飞书** ✅（你已有）→ 用来接收推送

---

## 第一步：获取 Gemini API Key（5分钟）

1. 打开 https://aistudio.google.com/app/apikey
2. 点击 **"Create API key"**
3. 复制那串 key（形如 `AIzaSy...`），**保存好，待会用**

---

## 第二步：创建飞书机器人 Webhook（5分钟）

1. 打开飞书，进入你想接收消息的**群聊**（没有就新建一个）
2. 点右上角 **"设置"** → **"机器人"** → **"添加机器人"**
3. 选 **"自定义机器人"**，随便起个名字（如"美股监控"）
4. 复制 **Webhook 地址**（形如 `https://open.feishu.cn/open-apis/bot/v2/hook/...`），**保存好**

---

## 第三步：上传代码到 GitHub（10分钟）

1. 打开 https://github.com，点右上角 **"+"** → **"New repository"**
2. 仓库名随便起（如 `stock-news-bot`），选 **Private（私有）**，点 **"Create repository"**
3. 点页面上的 **"uploading an existing file"**
4. 把本压缩包里的所有文件**全部拖进去**上传
5. 点 **"Commit changes"** 保存

---

## 第四步：配置密钥（最重要！3分钟）

> ⚠️ 密钥绝对不能直接写在代码里，要存在 GitHub Secrets

1. 在你的仓库页面，点 **"Settings"**（设置）
2. 左边菜单找 **"Secrets and variables"** → **"Actions"**
3. 点 **"New repository secret"**，添加以下三个：

| Name | Value |
|------|-------|
| `GEMINI_API_KEY` | 第一步复制的 Gemini Key |
| `FEISHU_WEBHOOK_URL` | 第二步复制的飞书 Webhook 地址 |
| `GROQ_API_KEY` | Groq API Key，用作 Gemini 频率限制时的备用引擎 |

> 这些值只放在 GitHub Secrets 里，不要写进代码、README、issue 或 commit。

---

## 第五步：启用 GitHub Actions（2分钟）

1. 在仓库页面点 **"Actions"** 标签
2. 如果看到提示"Workflows aren't running"，点 **"I understand my workflows, enable them"**
3. 你会看到两个 workflow：
   - **新闻监控（每20分钟）** — 实时推送
   - **每日早报晚报** — 8:00和20:00推送
4. 点任意一个 workflow → 点 **"Run workflow"** → **"Run workflow"** 手动测试一下

---

## 验证是否成功

- 手动触发后，等1-2分钟，飞书应该收到消息
- 如果没收到，点 Actions 页面那次运行记录，看红色错误提示

---

## 常见问题

**Q：GitHub Actions 每月免费额度够用吗？**
A：完全够。每20分钟跑一次，每次约30秒，一个月约 `72次/天 × 30天 × 0.5分钟 = 1080分钟`，免费额度是2000分钟，绰绰有余。

**Q：Gemini 免费额度够用吗？**
A：够。每天最多1500次请求，你实际用不到800次。

**Q：如何调整推送的严格程度？**
A：修改 `config.py` 里的 `PUSH_BULLISH_MIN`（看涨阈值）和 `PUSH_SCORE_MAX`（看跌阈值）。

**Q：如何增加或减少监控的新闻来源？**
A：修改 `config.py` 里的 `ALLOWED_SOURCES` 和 `BLOCKED_SOURCES` 列表。

**Q：仓库公开后会暴露我的推送记录吗？**
A：不会。运行状态保存在 GitHub Actions cache 里，`seen_ids.json` 和 `today_pushed.json` 不再提交到仓库。

---

> 💡 提示：第一次部署后，建议观察1-2天，根据实际收到的消息量调整 `config.py` 里的阈值。
