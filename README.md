# 🤖 Copilot Agent

一个基于 LangChain 的智能助手项目，提供联网搜索和 Excel 数据分析两种 Agent 模式。

## ✨ 功能特性

### 🌐 联网搜索 Agent
- 使用 DuckDuckGo 进行实时网络搜索
- 内置计算器工具
- 基于 Qwen 大语言模型生成准确、简洁的回答
- 获取最新信息并整合回答

### 📊 Excel 数据分析 Agent
- 自动读取 Excel 文件并分析数据结构
- 使用 Python + Pandas 进行数据处理和计算
- 提供数据摘要、统计信息和头部数据预览
- 基于真实数据给出分析结论

## 🏗️ 项目结构

```
copilot-agent/
├── src/
│   ├── agent.py          # 联网搜索 Agent 实现
│   ├── excel_agent.py    # Excel 数据分析 Agent 实现
│   ├── tools.py          # 工具集（搜索、计算器、Excel 读取、Python REPL）
│   ├── config.py         # 配置管理（从 .env 加载）
│   └── logger.py         # 日志配置
├── data/
│   └── test.xlsx         # 示例 Excel 文件
├── main.py               # 主入口程序
├── requirements.txt      # Python 依赖
├── .env                  # 环境变量配置
├── .env.local            # 本地环境变量（可选）
└── .gitignore
```

## 🚀 快速开始

### 前置要求

- Python 3.9+
- pip 包管理器

### 安装步骤

1. **克隆项目**
```bash
cd copilot-agent
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**

编辑 `.env` 文件，配置你的 LLM API 信息：

```env
# LLM 配置
MODEL_NAME="qwen-max"
MODEL_API_KEY="your-api-key-here"
MODEL_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"

# Agent 配置
VERBOSE=True
```

> **注意**: 本项目默认使用阿里云 Qwen 模型（DashScope）。你也可以修改为其他兼容 OpenAI API 的模型服务。

4. **运行程序**
```bash
python main.py
```

## 📖 使用指南

### 选择 Agent 模式

运行程序后，会出现交互式菜单：

```
==================================================
请选择Agent模式：
1 → 🌐 联网搜索Agent
2 → 📊 Excel数据分析Agent
==================================================
请输入数字 1/2 并回车
```

### 模式 1: 联网搜索 Agent

输入你的问题，Agent 会自动搜索网络并给出回答：

```
请输入你的问题：2024年人工智能最新发展趋势
```

### 模式 2: Excel 数据分析 Agent

输入数据分析问题（需包含文件路径）：

```
请输入数据分析问题（包含文件路径，如：data/test.xlsx）：
分析 data/test.xlsx 文件中的数据，给出销售总结
```

## 🛠️ 技术架构

### 核心框架

- **LangChain 1.2.15** - Agent 编排框架
- **LangChain OpenAI** - LLM 集成
- **LangChain Experimental** - Python REPL 工具

### LLM 模型

- 默认使用 **Qwen-Max**（阿里云通义千问）
- 支持任何兼容 OpenAI API 的模型服务
- 温度参数设置为 0，确保输出稳定性

### 工具集

#### 搜索 Agent 工具
- `DuckDuckGoSearchRun` - 网络搜索
- `calculator` - 数学计算

#### Excel Agent 工具
- `excel_reader` - Excel 文件读取和结构分析
- `PythonREPLTool` - Python 代码执行（用于 Pandas 数据分析）

## ⚙️ 配置说明

所有配置通过 `.env` 文件管理：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `MODEL_NAME` | 模型名称 | `qwen-max` |
| `MODEL_API_KEY` | API 密钥 | - |
| `MODEL_BASE_URL` | API 基础 URL | 阿里云 DashScope |
| `VERBOSE` | 是否显示详细日志 | `True` |

## 📝 示例

### Excel 数据分析示例

项目包含示例文件 `data/test.xlsx`，你可以尝试以下查询：

- "读取 data/test.xlsx 并分析数据结构"
- "计算 data/test.xlsx 中销售额的总和"
- "分析 data/test.xlsx 的销售趋势"

## 🔒 安全提示

- **不要将 `.env` 文件提交到版本控制系统**
- 项目已配置 `.gitignore` 忽略敏感信息
- 建议使用 `.env.local` 存储本地配置

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📮 联系方式

如有问题或建议，请提交 Issue。
