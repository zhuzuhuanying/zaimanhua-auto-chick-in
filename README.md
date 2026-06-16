# Zaimanhua Auto Check-in

基于 [ZAI_X](https://github.com/Fusn126/ZAI_X) 接口的再漫画 (zaimanhua.com) 每日任务自动化工具，使用 GitHub Actions 运行。

## 功能特性

### 每日任务

| 功能 | 对应工作流 | 说明 |
|-----|-----------|------|
| 每日综合任务 | Zaimanhua Daily Tasks | 一次完成 签到+评论+阅读 |
| 每日签到 | Zaimanhua Auto Check-in | 自动完成签到任务 |
| 每日评论 | Daily Comment plus | 在随机漫画下发表评论 |
| 每日阅读 | Daily Watch | 自动阅读漫画 |

### 已结束活动

| 功能 | 对应工作流 | 说明 |
|-----|-----------|------|
| 原创征稿季 | Yuanchuang Activity | 完成任务并自动抽奖 |
| 每日抽奖 | Daily Lottery | 完成任务并自动抽奖 |
| 51抽奖活动 | 51 Lottery Activity | 完成任务并自动抽奖 |
| 四周年活动 | 4th Anniversary Activity | 发送祝福 + 转盘抽奖 |
| 新年活动 | New Year Activity | 完成任务 + 祝福抽奖 |



## 配置 GitHub Secret

1. Fork 本仓库
2. 进入 **Settings** → **Secrets and variables** → **Actions**
3. 选择以下任一方式添加 Secret：

### 方式一：账号密码（推荐，自动登录）

| 用户名 Secret | 说明 | 密码 Secret | 说明 |
|---------------|------|-------------|------|
| `ZAIMANHUA_USERNAME` | 默认账号用户名/手机号 | `ZAIMANHUA_PASSWORD` | 默认账号密码 |
| `ZAIMANHUA_USERNAME_1` | 账号1用户名/手机号 | `ZAIMANHUA_PASSWORD_1` | 账号1密码 |
| `ZAIMANHUA_USERNAME_2` | 账号2用户名/手机号 | `ZAIMANHUA_PASSWORD_2` | 账号2密码 |
| `ZAIMANHUA_USERNAME_3` | 账号3用户名/手机号 | `ZAIMANHUA_PASSWORD_3` | 账号3密码 |
| `ZAIMANHUA_USERNAME_4` | 账号4用户名/手机号 | `ZAIMANHUA_PASSWORD_4` | 账号4密码 |
| `ZAIMANHUA_USERNAME_5` | 账号5用户名/手机号 | `ZAIMANHUA_PASSWORD_5` | 账号5密码 |

> 支持的工作流：
> - Zaimanhua Daily Tasks
> - Zaimanhua Auto Check-in
> - Daily Comment plus
> - Daily Watch
> - ~~Yuanchuang Activity~~
> - ~~51 Lottery Activity~~

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