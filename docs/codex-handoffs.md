# 可以直接发送给 Codex 的实施任务

## Mac mini

```text
请基于这个仓库完成 Mac mini 后端部署，实际执行而不只给建议。
先读 README.zh-CN.md、docs/mac-mini.md、SECURITY.md 和适用 AGENTS.md。
Hermes 已本地安装；保留现有 provider、profile、记忆、技能和聊天渠道。
先检查实际版本/配置/进程/服务/端口，备份后再修改；不盲目升级或覆盖。
复用现有 Gateway，启用 loopback API 和本机随机密钥，不启动重复 Gateway。
用 tools/init_env.py 生成片段并合并到正确 profile；不输出密钥。
安装或复用 Tailscale，必要登录由我完成。检查已有 Serve 配置，配置私网 HTTPS
到 Hermes loopback。保留 Bearer 鉴权，不用 Funnel、公网端口、exit node。
按当前 CLI 帮助实施，不覆盖其他 Serve 服务。复用现有服务管理，记录启动条件、
电源设置和回滚；说明重启/登录/FileVault 的实际限制。
执行 doctor、错误密钥、多轮历史和一个无副作用工具调用测试。
本机测试与 Windows/MacBook 外部测试分开记录，未执行的标为待验证。
填好 templates/CLIENT_SETUP.md 的私有副本，提供不含密钥的客户端接入信息。
将通用修复贡献回仓库；真实配置、密钥、日志和主机名留在仓库外或 .local/。
完成所有独立工作；仅登录、系统授权或影响现有服务的重大取舍需要我参与。
```

## Windows

```text
请基于这个仓库实际安装并联调桌宠。读 docs/desktop.md 和适用 AGENTS.md。
我会提供 Mac mini 的 CLIENT_SETUP；密钥在本机私密配置，不贴聊天。
检查 Windows/硬件/依赖，安装或复用 Tailscale，先用 doctor 验证远程 API。
独立安装上游 Open-LLM-VTuber 后端和匹配 Electron 客户端，记录版本与 commit。
参考配置片段合并完整配置，不用片段替换整个 conf.yaml。
让 openai_compatible_llm 连接实际 Hermes URL/model，禁用初期本地 MCP，
不另装 Hermes、不改用其他 LLM。先文字，再流式，再中文语音，再桌面宠物模式。
先用许可合适的示例 Live2D 模型；PNG 设定图不算已绑定模型。
查明中文 ASR/TTS 方案，说明模型下载体积和费用，不自动开通付费服务。
使用按键录音，测试嘴型、语音停止、回声、断网错误与恢复。
如 SSE 不兼容先记录脱敏失败再做最小修复；别预先增加代理。
验收连续对话、无副作用 Hermes 工具任务；不要将停止声音说成取消任务。
交付启动/停止/日志说明，填写 docs/validation.md 的真实测试结果。
所有私密配置留在仓库外，不提交密钥、机器地址和用户聊天内容。
```

## MacBook

```text
按 Windows 任务的目标，在 macOS 上选择匹配芯片的依赖和桌面客户端。
参考 docs/desktop.md，连接同一个 Mac mini 私网 API，不部署第二份 Hermes。
增加不同 Wi-Fi / 手机热点下的测试。第一版聊天历史独立；不宣称自动跨设备续聊。
记录版本、启动方式和实测结果，密钥留在本机。
```
