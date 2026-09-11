# Mac mini 部署

先阅读 [安全说明](../SECURITY.md)。本指南假设 Hermes 已本地安装。
API 参数参考 [当前官方文档](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/)，
必须以本机实际版本为准。不要直接覆盖现有 profile。

## 1. 清点和备份

检查 `hermes --help`、安装版本、活动 profile、Gateway 启动方式和端口。
检查 `tailscale status`、`tailscale serve status`（需要客户端 CLI 可用）。
先备份实际配置及服务定义；不要在日志中打印环境变量或密钥。
如果当前 Gateway 已启动，应复用并受控重启，不运行第二份共享同一配置目录的服务。

## 2. API 配置

从仓库根目录运行：

```bash
python3 tools/init_env.py --output .local/hermes-api.env
```

默认生成 loopback:8642 和 32 字节随机密钥。端口冲突可加 `--port 8643`。
将片段合并到活动 profile 对应环境文件，而不是假定所有人都使用 `~/.hermes`。
现有模型提供商、记忆、技能和聊天渠道保持不变。
按安装版本的服务方式启动/重启 Gateway；前台文档示例为 `hermes gateway`。

本机检查（密钥隐藏输入，不需要放进命令参数）：

```bash
python3 tools/doctor.py --base-url http://127.0.0.1:8642/v1
python3 tools/doctor.py --base-url http://127.0.0.1:8642/v1 --chat --stream
```

## 3. 私网访问

从 [官方来源](https://tailscale.com/download) 安装 Tailscale，三台设备登录同一 tailnet。
如果有其他用户/共享设备，限制访问策略到目标客户端。
确认没有冲突的 Serve 服务后，按当前 `tailscale serve --help` 配置 loopback 代理。
当前常见命令如下，已有配置时不要直接覆盖：

```bash
tailscale serve --bg http://127.0.0.1:8642
tailscale serve status
```

如 CLI 要求启用 HTTPS，按官方交互流程完成。记录实际输出的 HTTPS URL，
在其后加 `/v1` 供客户端使用。不要启用 Funnel、exit node 或子网路由。
Serve 使用条件和不同 macOS 客户端差异见 [官方文档](https://tailscale.com/docs/features/tailscale-serve)。

## 4. 持续运行和回滚

复用 Hermes 服务管理；如需 launchd，使用实际可执行文件的绝对路径和明确的工作目录。
记录是登录启动还是开机启动。保持插电联网、避免系统自动睡眠，允许显示器休眠。
FileVault 重启后可能需要本地解锁；未经测试不能宣称断电后全自动恢复。

回滚：停止新加服务、恢复备份配置、只移除本项目新增的 Serve 路由，并恢复记录过的
电源设置。不要使用全局 Serve reset 清除其他服务。不要删除 Hermes 数据目录。

## 5. 交付给客户端

填写 [连接信息模板](../templates/CLIENT_SETUP.md)。密钥通过密码管理器或其他私密渠道
传递，不放进提交、公开 issue 或聊天。使用实际 model ID，不猜测它一定为 hermes-agent。
本机成功后还需要 Windows 和手机热点下的 MacBook 验证。
