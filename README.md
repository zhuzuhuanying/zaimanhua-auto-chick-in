# Zaimanhua Auto Check-in

基于 GitHub Actions 的再漫画 (zaimanhua.com) 每日任务自动化工具。

## 功能特性

### 每日任务

| 功能 | 说明 | 触发时间 (北京) |
|-----|------|----------------|
| 每日签到 | 自动完成签到任务、领取积分、领取VIP福利 | 8:00 |
| 每日评论 | 在随机漫画下发表评论 | 9:30 |
| 每日阅读 | 自动阅读漫画 | 10:00 |
| 原创征稿季 | 完成任务并自动抽奖 | 15:30 |

### 已结束活动

| 功能 | 说明 | 触发时间 (北京) |
|-----|------|----------------|
| 每日抽奖 | 完成任务并自动抽奖 | 11:00 |
| 51抽奖活动 | 完成任务并自动抽奖 | 15:00 |
| 四周年活动 | 发送祝福 + 转盘抽奖 | 5:00-23:00 每20分钟 |
| 新年活动 | 完成任务 + 祝福抽奖 | 8:00-23:00 每15分钟 |

> **注意！活动已结束**

### 其他

| 功能 | 说明 | 触发时间 (北京) |
|-----|------|----------------|
| ESJ论坛水经验 | 自动水经验 | 6:00 |

> **自用，可忽略**

## 配置 GitHub Secret

1. Fork 本仓库
2. 进入 **Settings** → **Secrets and variables** → **Actions**
3. 选择以下任一方式添加 Secret：

### 方式一：账号密码（推荐，自动登录）

| Secret 名称 | 说明 |
|------------|------|
| `ZAIMANHUA_USERNAME` / `ZAIMANHUA_PASSWORD` | 默认账号 |
| `ZAIMANHUA_USERNAME_1` / `ZAIMANHUA_PASSWORD_1` | 账号 1 |
| `ZAIMANHUA_USERNAME_2` / `ZAIMANHUA_PASSWORD_2` | 账号 2 |
| `ZAIMANHUA_USERNAME_3` / `ZAIMANHUA_PASSWORD_3` | 账号 3 |
| `ZAIMANHUA_USERNAME_4` / `ZAIMANHUA_PASSWORD_4` | 账号 4 |
| `ZAIMANHUA_USERNAME_5` / `ZAIMANHUA_PASSWORD_5` | 账号 5 |

> 支持的工作流：Zaimanhua Auto Check-in、Daily Comment plus、Daily Watch、Yuanchuang Activity、51 Lottery Activity（51活动已结束）

### 方式二：手动配置 Cookie

| Secret 名称 | 说明 |
|------------|------|
| `ZAIMANHUA_COOKIE` | 默认账号 |
| `ZAIMANHUA_COOKIE_1` | 账号 1 |
| `ZAIMANHUA_COOKIE_2` | 账号 2 |
| `ZAIMANHUA_COOKIE_3` | 账号 3 |
| `ZAIMANHUA_COOKIE_4` | 账号 4 |
| `ZAIMANHUA_COOKIE_5` | 账号 5 |

4. 进入 **Actions** 标签，点击启用 workflows
5. 任务将按计划自动运行，也可手动触发测试
