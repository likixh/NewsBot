# US Stock News Monitor Bot

<p align="center">
  <a href="#中文"><kbd>中文</kbd></a>
  <a href="#english"><kbd>English</kbd></a>
</p>

An automated news monitor for US stock market signals. It collects market news from RSS sources, uses Gemini with Groq as a fallback to score market impact, and sends alerts or daily summaries to a Feishu group.

---

## 中文

### 功能

- 监控 Reuters、SEC Filing、earnings 相关 RSS 新闻源
- 用 Gemini 分析新闻对美股、板块、ETF、大宗商品的影响
- Gemini 触发频率限制或失败时，自动切换到 Groq
- 通过飞书自定义机器人推送看涨/看跌信号
- 支持早报/晚报，汇总当天已推送信号和市场背景
- 运行状态保存在 GitHub Actions cache，不会提交推送记录到公开仓库

### 准备

需要准备：

- GitHub 账号，用来 fork 仓库和运行 GitHub Actions
- Google AI Studio API key，用来调用 Gemini
- Groq API key，用作备用 LLM 引擎
- 飞书群聊和自定义机器人 webhook，用来接收推送

### 1. Fork 仓库

打开本仓库页面，点击右上角 **Fork**，把项目复制到自己的 GitHub 账号下。

也可以 clone 到本地后推送到自己的仓库：

```bash
git clone https://github.com/likixh/NewsBot.git
cd NewsBot
```

### 2. 获取 API Key

Gemini:

1. 打开 https://aistudio.google.com/app/apikey
2. 点击 **Create API key**
3. 保存生成的 key

Groq:

1. 打开 https://console.groq.com/keys
2. 创建 API key
3. 保存生成的 key

### 3. 创建飞书 Webhook

1. 打开飞书群聊
2. 进入 **设置** -> **机器人** -> **添加机器人**
3. 选择 **自定义机器人**
4. 复制 webhook 地址，格式类似 `https://open.feishu.cn/open-apis/bot/v2/hook/...`

### 4. 配置 GitHub Secrets

不要把任何 key 写进代码、README、issue 或 commit。把它们放到 GitHub Secrets：

1. 打开 fork 后的仓库
2. 进入 **Settings** -> **Secrets and variables** -> **Actions**
3. 点击 **New repository secret**
4. 添加：

| Name | Value |
| --- | --- |
| `GEMINI_API_KEY` | Gemini API key |
| `GROQ_API_KEY` | Groq API key |
| `FEISHU_WEBHOOK_URL` | 飞书机器人 webhook |

### 5. 运行 Workflow

本仓库默认只保留手动运行，避免 fork 后立刻自动消耗 API 额度。

手动运行：

1. 打开仓库的 **Actions** 页面
2. 选择 **News Monitor** 或 **Daily Market Report**
3. 点击 **Run workflow**

开启定时运行：

在 `.github/workflows/monitor.yml` 里加回 cron：

```yaml
on:
  schedule:
    - cron: '0,20,40 16-23 * * *'
    - cron: '0,20,40 0-4 * * *'
  workflow_dispatch:
```

在 `.github/workflows/daily_report.yml` 里加回早晚报 cron：

```yaml
on:
  schedule:
    - cron: '0 17 * * *'
    - cron: '0 5 * * *'
  workflow_dispatch:
```

GitHub Actions 使用 UTC 时间。上面的示例大致覆盖美股盘中和盘后时段，使用前请按自己的时区调整。

### 配置

常用配置在 `config.py`：

- `PUSH_SCORE_MAX`：看跌推送阈值上限
- `PUSH_BULLISH_MIN`：看涨推送阈值下限
- `ALLOWED_SOURCES`：允许的新闻来源关键词
- `BLOCKED_SOURCES`：排除的新闻来源关键词
- `MAX_SEEN_IDS`：去重历史保留数量

### 状态文件

`seen_ids.json` 和 `today_pushed.json` 是运行时状态文件。它们会在 Actions 运行时生成，并通过 Actions cache 保存。

这些文件已被 `.gitignore` 忽略，不会提交到公开仓库。

### 安全

- 不要提交 `.env`、API key、webhook URL 或任何私钥
- 建议开启 GitHub Secret Scanning 和 Push Protection
- 如果 key 曾经被提交过，立即在对应平台 revoke 并重新生成

### License

MIT License.

---

## English

### Features

- Monitors Reuters, SEC filing, and earnings-related RSS feeds
- Uses Gemini to analyze market impact across stocks, sectors, ETFs, and commodities
- Falls back to Groq when Gemini is rate-limited or unavailable
- Sends bullish and bearish alerts to a Feishu group bot
- Generates morning and evening market summaries
- Keeps runtime state in GitHub Actions cache instead of committing alert history to the public repository

### Requirements

You need:

- A GitHub account for forking the repository and running GitHub Actions
- A Google AI Studio API key for Gemini
- A Groq API key as the fallback LLM provider
- A Feishu group and custom bot webhook for receiving alerts

### 1. Fork The Repository

Open this repository on GitHub and click **Fork**.

You can also clone it locally:

```bash
git clone https://github.com/likixh/NewsBot.git
cd NewsBot
```

### 2. Get API Keys

Gemini:

1. Open https://aistudio.google.com/app/apikey
2. Click **Create API key**
3. Save the generated key

Groq:

1. Open https://console.groq.com/keys
2. Create an API key
3. Save the generated key

### 3. Create A Feishu Webhook

1. Open a Feishu group chat
2. Go to **Settings** -> **Bots** -> **Add Bot**
3. Select **Custom Bot**
4. Copy the webhook URL, which looks like `https://open.feishu.cn/open-apis/bot/v2/hook/...`

### 4. Configure GitHub Secrets

Never put keys in code, README files, issues, or commits. Store them in GitHub Secrets:

1. Open your forked repository
2. Go to **Settings** -> **Secrets and variables** -> **Actions**
3. Click **New repository secret**
4. Add:

| Name | Value |
| --- | --- |
| `GEMINI_API_KEY` | Gemini API key |
| `GROQ_API_KEY` | Groq API key |
| `FEISHU_WEBHOOK_URL` | Feishu bot webhook |

### 5. Run Workflows

This repository defaults to manual runs so forks do not immediately spend API quota.

Manual run:

1. Open the repository **Actions** tab
2. Select **News Monitor** or **Daily Market Report**
3. Click **Run workflow**

Enable scheduled runs:

Add cron back to `.github/workflows/monitor.yml`:

```yaml
on:
  schedule:
    - cron: '0,20,40 16-23 * * *'
    - cron: '0,20,40 0-4 * * *'
  workflow_dispatch:
```

Add morning and evening report cron to `.github/workflows/daily_report.yml`:

```yaml
on:
  schedule:
    - cron: '0 17 * * *'
    - cron: '0 5 * * *'
  workflow_dispatch:
```

GitHub Actions uses UTC. Adjust the schedule for your own timezone and market window.

### Configuration

Common settings live in `config.py`:

- `PUSH_SCORE_MAX`: upper threshold for bearish alerts
- `PUSH_BULLISH_MIN`: lower threshold for bullish alerts
- `ALLOWED_SOURCES`: allowed source keywords
- `BLOCKED_SOURCES`: blocked source keywords
- `MAX_SEEN_IDS`: deduplication history size

### Runtime State

`seen_ids.json` and `today_pushed.json` are runtime state files. They are created during workflow runs and stored via GitHub Actions cache.

They are ignored by `.gitignore` and are not committed to the public repository.

### Security

- Do not commit `.env` files, API keys, webhook URLs, or private keys
- Enable GitHub Secret Scanning and Push Protection
- If a key was ever committed, revoke it and generate a new one

### License

MIT License.
