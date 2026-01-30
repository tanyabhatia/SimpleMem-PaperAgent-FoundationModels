# SimpleMem PaperAgent 🧠

> **Semantic Lossless Compression Memory System for LLM Agents**

A Model Context Protocol (MCP) implementation of [SimpleMem](https://github.com/aiming-lab/SimpleMem) - the state-of-the-art memory system achieving **43.24% F1** on LoCoMo-10 benchmark with **30× token reduction**.

[![Paper](https://img.shields.io/badge/📄_Paper-arXiv-b31b1b?style=flat-square)](https://arxiv.org/abs/2601.02553)
[![GitHub](https://img.shields.io/badge/GitHub-SimpleMem-181717?logo=github&style=flat-square)](https://github.com/aiming-lab/SimpleMem)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## 🎯 What is SimpleMem?

SimpleMem transforms how LLM agents handle long-term memory through a three-stage pipeline:

1. **Semantic Compression** - Filters noise, resolves references ("tomorrow" → "2025-01-30")
2. **Multi-View Indexing** - Semantic + Lexical + Symbolic retrieval layers  
3. **Adaptive Retrieval** - Query complexity drives search depth

**Result:** 26.4% better recall than baselines, 30× fewer tokens.

---

## ⚡ Quick Start

### Option 1: Use Cloud Service (Easiest)

1. Register at https://mcp.simplemem.cloud
2. Get your Bearer token
3. Add to Claude Desktop config:

```json
{
  "mcpServers": {
    "simplemem": {
      "url": "https://mcp.simplemem.cloud/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN"
      }
    }
  }
}
```

### Option 2: Run Locally (This PaperAgent)

```bash
# 1. Install dependencies
pip install mcp

# 2. Configure Claude Desktop
# Edit: ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)
# Or: %APPDATA%\Claude\claude_desktop_config.json (Windows)

{
  "mcpServers": {
    "simplemem-paperagent": {
      "command": "python",
      "args": ["/absolute/path/to/simplemem_mcp_server.py"]
    }
  }
}

# 3. Restart Claude Desktop
# Look for 🔌 icon to confirm connection
```

---

## 📁 Files in This PaperAgent

```
SimpleMem_PaperAgent/
├── README.md                              # This file
├── SimpleMem_PaperAgent_Documentation.md  # Detailed paper explanation
├── SimpleMem_Setup_Guide.md               # Full setup & usage guide
├── simplemem_mcp_server.py                # MCP server implementation
├── claude_desktop_config.example.json     # Example config
└── requirements.txt                       # Python dependencies
```

---

## 🚀 Usage Example

**Store a conversation:**
```
User → Claude: Remember this. Alice said "Let's meet at Starbucks tomorrow 
               at 2pm." Bob replied "Sure, I'll bring the report."

Claude: [Uses add_dialogues_batch + finalize_memory tools]
        Stored in memory with semantic compression.
```

**Query later:**
```
User → Claude: When and where will Alice and Bob meet?

Claude: [Uses ask_memory tool with adaptive retrieval]
        Alice and Bob will meet at Starbucks on January 30, 2025 at 2:00 PM.
        Bob will bring the report.
```

---

## 🔧 Available Tools

| Tool | Description |
|------|-------------|
| `add_dialogue` | Add single conversation turn |
| `add_dialogues_batch` | Add multiple turns (recommended) |
| `finalize_memory` | Process buffered dialogues ⚠️ **Always call after adding!** |
| `ask_memory` | Query with adaptive retrieval |
| `get_memory_stats` | View system statistics |
| `get_atomic_entries` | Inspect raw memory atoms |
| `clear_memory` | Reset all memory |

---

## 📊 Performance (LoCoMo-10 Benchmark)

| Metric | SimpleMem | Best Baseline | Improvement |
|--------|-----------|---------------|-------------|
| **F1 Score** | 43.24% | 34.20% (Mem0) | **+26.4%** |
| **Tokens** | ~550 | ~16,500 | **30× less** |
| **Retrieval Time** | 388s | 583s (Mem0) | **33% faster** |

---

## 📚 Documentation

- **[SimpleMem_PaperAgent_Documentation.md](SimpleMem_PaperAgent_Documentation.md)** - Complete paper explanation
  - Problem statement & solution
  - Architecture details (3-stage pipeline)
  - Performance metrics
  - Technical implementation
  - Related work comparison
  
- **[SimpleMem_Setup_Guide.md](SimpleMem_Setup_Guide.md)** - Setup & usage
  - Installation (cloud vs local)
  - Configuration (Claude Desktop, Cursor)
  - Usage examples (basic to advanced)
  - Troubleshooting
  - Advanced topics

---

## 🛠️ Production Deployment

This PaperAgent includes a **mock implementation** for demonstration. For production use:

```bash
# Clone the full SimpleMem repository
git clone https://github.com/aiming-lab/SimpleMem.git
cd SimpleMem

# Install dependencies
pip install -r requirements.txt

# Configure (add OpenAI/Qwen API key)
cp config.py.example config.py
# Edit config.py

# Modify simplemem_mcp_server.py to use real SimpleMem
# Replace: MockSimpleMemSystem
# With: from main import SimpleMemSystem
```

---

## 🏗️ Architecture Overview

```
┌─────────────────────────┐
│   MCP Client            │
│   (Claude Desktop)      │
└───────────┬─────────────┘
            │ JSON-RPC/STDIO
            ▼
┌─────────────────────────────────┐
│   SimpleMem MCP Server          │
│   (This PaperAgent)             │
│   - Tool handlers               │
│   - Input validation            │
└───────────┬─────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│   SimpleMem Core                │
│   Stage 1: Semantic Compression │
│   Stage 2: Multi-View Indexing  │
│   Stage 3: Adaptive Retrieval   │
└─────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│   LanceDB Vector Store          │
│   - Atomic facts                │
│   - 1024-d embeddings           │
│   - Hybrid indexes              │
└─────────────────────────────────┘
```

---

## 📖 Citation

```bibtex
@article{simplemem2025,
  title={SimpleMem: Efficient Lifelong Memory for LLM Agents},
  author={Liu, Jiaqi and Su, Yaofeng and Xia, Peng and Zhou, Yiyang and 
          Han, Siwei and Zheng, Zeyu and Xie, Cihang and Ding, Mingyu and 
          Yao, Huaxiu},
  journal={arXiv preprint arXiv:2601.02553},
  year={2025},
  url={https://github.com/aiming-lab/SimpleMem}
}
```

---

## 🔗 Links

- **Paper:** https://arxiv.org/abs/2601.02553
- **Original GitHub:** https://github.com/aiming-lab/SimpleMem
- **Cloud MCP:** https://mcp.simplemem.cloud
- **Project Page:** https://aiming-lab.github.io/SimpleMem-Page
- **Discord:** https://discord.gg/KA2zC32M

---

## 📧 Contact

**PaperAgent Maintainer:** Tanya  
**Affiliation:** Stanford University, MS Biomedical Data Science  
**Research:** Bias detection in clinical AI systems, digital health

For SimpleMem questions:
- Join Discord: https://discord.gg/KA2zC32M
- GitHub Issues: https://github.com/aiming-lab/SimpleMem/issues

---

## 📄 License

MIT License - Same as SimpleMem

```
Copyright (c) 2025 SimpleMem Authors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

**Built with ❤️ for the AI research community**

*SimpleMem: Because your AI agent deserves a better memory than goldfish* 🐠→🧠
