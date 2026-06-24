# NextUSinger Studio

NextUSinger Studio 是一个面向歌唱合成爱好者/开发者的开源原型：它提供类似 Synthesizer V / OpenUtau 的本地编辑器思路，支持导入 DiffSinger/OpenVPI 风格声库目录或 ZIP，并通过可插拔后端进行歌唱合成、音频导出和 AI 辅助创作。

> 重要：本仓库**不内置任何声库、模型权重或第三方 DiffSinger 代码**。你需要自行准备拥有授权的 DiffSinger/OpenVPI 声库和推理环境。请不要用未经同意的声音模型生成真人、名人、公众人物或任何可能侵权/冒充的声音。

## 已完成的原型能力

- **声库导入**：扫描本地目录，识别 `config.yaml/json`、`.ckpt/.pth/.pt/.onnx`、vocoder、variance/f0/pitch/energy/breathiness 等文件，并生成统一 manifest。
- **ZIP 声库导入**：支持网页上传 `.zip` 到 FastAPI 服务端，也支持 CLI 直接导入 ZIP；后端会安全解压到 `NEXTUSINGER_HOME/imported_voicebanks` 后注册 manifest。
- **工程模型**：支持音符、歌词、phoneme、velocity、gender、tension、breathiness、energy、pitch curve、tempo 等字段。
- **后端 API**：FastAPI 提供 voicebank、project、synthesis、AI endpoints。
- **音频导出**：无真实模型时可生成 mock WAV，方便 UI/流程联调；安装 DiffSinger 后可启用外部推理适配器。
- **DiffSinger 适配层**：将 NextUSinger 工程转换为通用 score JSON，支持调用外部 `NEXTUSINGER_DIFFSINGER_CMD`。
- **AI 功能入口**：歌词续写、phoneme 草稿、自动音高平滑、和声生成、工程诊断均已提供本地规则版；可替换为云端/本地 LLM。
- **前端雏形**：React + Vite，本地网页工作站，可导入声库路径、上传 ZIP、编辑音符、调用 AI、导出 WAV。
- **钢琴卷帘升级**：加入 MIDI/音名标号、小节号、八分/十六分参考线、点击轨道建立音符、吸附网格、默认音符长度与音符增删/伸缩。
- **测试**：包含 voicebank 扫描、ZIP 导入安全性与 AI 调音单元测试。

## 目录结构

```text
NextUSinger/
  backend/              Python FastAPI 后端与合成适配层
  frontend/             React/Vite 编辑器原型
  electron/             可选 Electron 桌面包装
  docs/                 架构、声库格式、发布说明
  examples/             示例工程与示例声库目录
  scripts/              启动、CLI 渲染/声库导入脚本
```

## 快速启动

### 1. 启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn nextusinger.main:app --reload --port 7860
```

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 Vite 提示的本地地址。默认后端地址为 `http://127.0.0.1:7860`。

### 3. 导入声库

本地目录导入：

```bash
python scripts/import_voicebank_cli.py /path/to/diffsinger_voicebank
```

ZIP 导入并注册到服务端存储：

```bash
python scripts/import_voicebank_cli.py /path/to/voicebank.zip
```

只扫描、不保存 manifest：

```bash
python scripts/import_voicebank_cli.py /path/to/voicebank.zip --no-save
```

网页端也可以在「声库」面板中选择 `.zip` 并上传。ZIP 会被后端安全解压，拒绝绝对路径或 `../` 路径穿越条目。

### 4. 命令行渲染示例

```bash
python scripts/render_cli.py examples/demo_project.nextu.json --out out/demo.wav
```

没有真实 DiffSinger 环境时会生成可听的 mock WAV；这用于验证工程链路，不代表最终声库音色。

## 接入真实 DiffSinger/OpenVPI 推理

本项目默认不复制 DiffSinger 源码，避免许可证/模型权重混淆。推荐做法：

1. 安装你选择的 DiffSinger/OpenVPI 推理环境。
2. 导入一个已授权声库目录或 ZIP。
3. 设置环境变量，让 NextUSinger 调用外部命令：

```bash
export NEXTUSINGER_DIFFSINGER_CMD="python /path/to/your/infer.py --score {score_json} --voicebank {voicebank_dir} --out {output_wav}"
```

占位符说明：

- `{score_json}`：NextUSinger 生成的中间 score JSON。
- `{voicebank_dir}`：导入声库原始目录或 ZIP 解压后的目录。
- `{output_wav}`：后端期望生成的 WAV 路径。

如果命令返回成功并写出 WAV，API 会把它作为最终渲染结果返回；否则自动回退到 mock engine，方便调试。

## API 速览

- `GET /api/health`
- `POST /api/voicebanks/import`：导入本地声库目录
- `POST /api/voicebanks/import-zip`：上传并导入 `.zip` 声库
- `GET /api/voicebanks`：列出已导入声库
- `POST /api/synthesis/render`：渲染 WAV
- `POST /api/ai/lyrics`：歌词建议
- `POST /api/ai/phonemes`：phoneme 草稿
- `POST /api/ai/tune`：音高曲线平滑/人性化
- `POST /api/ai/harmony`：生成三度/五度和声草稿
- `POST /api/ai/diagnose`：工程问题诊断

## 许可证

NextUSinger Studio 本身使用 MIT License。第三方代码、模型、声库、音频样本需遵守其各自许可证与使用条款。
