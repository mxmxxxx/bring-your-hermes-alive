# Windows / MacBook 桌宠

前置：取得 Mac mini 的连接信息与密钥；Tailscale 已登录。

## 1. 先检查 API

安装 Python 3.10+。在仓库根目录执行（Windows 可用 `py -3`，macOS 用 `python3`）：

```bash
python tools/doctor.py --base-url https://YOUR-HOST.YOUR-TAILNET.ts.net/v1 --chat --stream
```

模型不唯一时指定 `--model`。401/403 先检查密钥和访问策略，连接失败先检查 Mac mini
是否在线、Tailscale、Serve 与主机防火墙，不要关闭整个防火墙。

## 2. 安装上游

按 [官方快速开始](https://docs.llmvtuber.com/en/docs/quick-start/) 安装
Open-LLM-VTuber **后端及匹配版本的 Electron 客户端**。Windows 下载对应 exe，
MacBook 下载适合芯片的 macOS 包。保留安装版本与上游 commit ID。
使用独立环境，不复制本仓库的 Python 版本要求作为上游版本要求。

可按官方仓库说明获取源码（克隆本身不安装依赖）：

```bash
git clone --recursive https://github.com/Open-LLM-VTuber/Open-LLM-VTuber.git
```

在该项目目录按其文档完成依赖和启动；本项目不固定未经实测的上游版本。

## 3. 合并配置

备份上游本地 `conf.yaml`。参考 [配置片段](../configs/vtuber-hermes.fragment.yaml)
把相应字段合并到上游完整模板；**不能用片段替换整个文件**。
设置实际 Base URL、model ID 和私有密钥；不要假设 `${ENV_VAR}` 会自动展开。
保留 ASR/TTS 和模型字段。初期禁用桌宠本地 MCP 工具，让任务统一在 Hermes 执行。

先使用有适用许可的示例模型。文字聊天需要正确的 messages 历史；Hermes 自定义
SSE 事件必须被忽略或正确解析，不应作为语音正文。若出现不兼容，记录脱敏错误，
再做最小适配，不预先引入代理。

## 4. 中文语音

选择上游当前支持、适合硬件的中文 ASR 和 TTS。先按键/点击录音，再考虑免提。
语音模型可能需要额外下载；云端 TTS 可能需要账号和费用，不能假定免费或离线。
避免扬声器回声，先用耳机测试。检查嘴型、长回复分句、停止播放与重连。
停止声音并不保证 Hermes 的工具任务停止；第一版不承诺远程取消。

可将 [人设提示词](../configs/persona.zh-CN.txt) 放入桌宠角色配置，不修改 Hermes 全局人格。

## 5. MacBook 与任务边界

在外部 Wi-Fi / 手机热点测试相同 HTTPS 地址。Mac mini 必须持续在线。
两个客户端暂不共享聊天记录；Hermes 的服务端会话 API 需要另行适配后才能用于续聊。
人物随任务状态变化、点击摸头反应和重启后自动连接需要按实际模型/客户端能力验收。
