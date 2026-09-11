# Bring Your Hermes Alive

让你的 Hermes 拥有可以对话的 Live2D 桌面形象，在家用 Windows，出门用 MacBook。

**当前是早期部署工具包，不是一键安装成品。** 工具具有离线测试；真实设备上的
Hermes、Tailscale、语音和 Live2D 联调仍待完成。本项目不附带已绑定的角色模型。

## 每台设备运行什么

| 设备 | 软件 | 职责 |
| --- | --- | --- |
| Mac mini | 已有 Hermes + Gateway/API | 对话、记忆、工具执行 |
| Mac mini | Tailscale + Serve | 私网 HTTPS 访问入口 |
| Windows | Tailscale + Open-LLM-VTuber 后端和桌面客户端 | 人物、语音识别、语音播放 |
| MacBook | 同上，使用 macOS 版本 | 外出访问同一个 Hermes |

语音配套后端运行在使用桌宠的电脑，不需要在这些电脑再装 Hermes 或本地大语言模型。
Hermes 默认仍在 Mac mini 执行任务；控制 Windows 需要另行添加执行工具。
同一个后端不代表两个客户端自动同步聊天记录。

## 开始复刻

1. Fork 仓库，再 clone 你自己的仓库。安装 Python 3.10+，本仓库工具无需 pip 依赖。
2. 按 [Mac mini 指南](docs/mac-mini.md) 部署；或直接发送 [Mac mini Codex 任务](docs/codex-handoffs.md)。
3. 取得实际 Base URL 和 model ID；密钥只在本机保存和安全传递。
4. 按 [Windows / MacBook 指南](docs/desktop.md) 安装桌宠和配套后端。
5. 先用有使用许可的示例 Live2D 模型完成文字、语音联调。
6. 按 [角色制作说明](docs/live2d.md) 替换专属人物。

检查连接（Windows 可用 `py -3`，macOS 通常用 `python3` 代替 `python`）：

```bash
python tools/doctor.py --base-url https://YOUR-HOST.YOUR-TAILNET.ts.net/v1
```

程序隐藏输入 API 密钥。默认只检查模型列表；`--chat` 和 `--stream` 分别发起一次
真实推理请求，可能产生模型费用。不会打印回复正文或密钥。

创建环境配置片段：

```bash
python tools/init_env.py --output .local/hermes-api.env
```

只创建新文件，不自动修改 Hermes；已有目标文件会拒绝覆盖。先备份配置，再合并到
当前 profile 的配置中。配置文件不会被工具自动加载，医生工具也不会读取 `.env`。

验收请填写 [验证清单](docs/validation.md)，未实测项目保持待验证，不要承诺已经可用。

## 当前交付

- 双机与跨网络部署文档、Codex 交接任务。
- Hermes 配置生成器、OpenAI 兼容 API 检查工具。
- 桌宠配置片段、人物性格提示词、测试与 CI。
- 路线图、贡献指南、MIT 许可证。

上游软件及角色资源单独下载，遵循各自许可。我们不会把概念图冒充 Live2D 模型，
也不会把中断语音播放等同于取消 Agent 任务。

官方参考链接与项目关系见 [English README](README.md#upstream-projects)。
