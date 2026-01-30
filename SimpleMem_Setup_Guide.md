# SimpleMem PaperAgent - Setup & Usage Guide

## 🎯 Overview

This is a **PaperAgent implementation** of SimpleMem, providing access to the semantic lossless compression memory system through the Model Context Protocol (MCP).

**What is SimpleMem?**
- Paper: "SimpleMem: Efficient Lifelong Memory for LLM Agents" (Liu et al., 2025)
- 43.24% F1 score on LoCoMo-10 benchmark (26.4% improvement over baselines)
- 30× token reduction through semantic compression
- Multi-view hybrid retrieval (semantic + lexical + symbolic)

---

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- Node.js 18+ (for local MCP deployment)
- Claude Desktop OR Cursor IDE (as MCP client)

### Option 1: Cloud Service (Easiest)

Use the hosted SimpleMem MCP server at https://mcp.simplemem.cloud

**Steps:**
1. Register for an account at https://mcp.simplemem.cloud
2. Get your Bearer token
3. Add to Claude Desktop config (see Configuration section)

### Option 2: Local Deployment (This PaperAgent)

**Step 1: Install Python Dependencies**

```bash
# Clone or download this PaperAgent
cd /path/to/SimpleMem_PaperAgent

# Install MCP SDK
pip install mcp

# For production SimpleMem (optional):
git clone https://github.com/aiming-lab/SimpleMem.git
cd SimpleMem
pip install -r requirements.txt
```

**Step 2: Test the Server**

```bash
# Test with MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Run server
python simplemem_mcp_server.py

# In another terminal
npx @modelcontextprotocol/inspector python simplemem_mcp_server.py
```

---

## ⚙️ Configuration

### Claude Desktop Setup

**Location of config file:**
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**Configuration:**

```json
{
  "mcpServers": {
    "simplemem-paperagent": {
      "command": "python",
      "args": ["/absolute/path/to/simplemem_mcp_server.py"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**For cloud service:**
```json
{
  "mcpServers": {
    "simplemem": {
      "url": "https://mcp.simplemem.cloud/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN_HERE"
      }
    }
  }
}
```

### Cursor IDE Setup

**Location:** `.cursor/mcp_config.json` in your workspace

```json
{
  "mcpServers": {
    "simplemem-paperagent": {
      "command": "python",
      "args": ["/absolute/path/to/simplemem_mcp_server.py"]
    }
  }
}
```

**After configuration:**
1. Restart Claude Desktop or Cursor
2. Look for 🔌 icon indicating MCP connection
3. Click to see available tools

---

## 🚀 Usage Examples

### Example 1: Basic Conversation Memory

**User → Claude:**
```
Remember this conversation:
Alice: "Bob, let's meet at Starbucks tomorrow at 2pm"
Bob: "Sure, I'll bring the market analysis report"
```

**Claude uses tools:**
```json
// Tool: add_dialogues_batch
{
  "dialogues": [
    {
      "speaker": "Alice",
      "content": "Bob, let's meet at Starbucks tomorrow at 2pm",
      "timestamp": "2025-01-29T14:30:00"
    },
    {
      "speaker": "Bob", 
      "content": "Sure, I'll bring the market analysis report",
      "timestamp": "2025-01-29T14:31:00"
    }
  ]
}

// Tool: finalize_memory
{}
```

**Later, User asks:**
```
When and where will Alice and Bob meet?
```

**Claude uses tool:**
```json
// Tool: ask_memory
{
  "query": "When and where will Alice and Bob meet?",
  "top_k": 5
}
```

**SimpleMem response:**
```
Alice and Bob will meet at Starbucks on January 30, 2025 at 2:00 PM.
Bob will bring the market analysis report.
```

---

### Example 2: Multi-Session Research Project

**Session 1 - Literature Review:**
```
User: I'm researching bias detection in clinical AI systems for my ICML paper

Claude: [add_dialogue] → [finalize_memory]
Stored: "User is working on ICML paper about bias detection in clinical AI"
```

**Session 2 - Methodology (next day):**
```
User: I'm using multi-agent simulations to test postoperative pain management

Claude: [ask_memory "research project"] 
         → Retrieves: ICML paper, bias detection, clinical AI
[add_dialogue] → [finalize_memory]
Stored: "Multi-agent simulation methodology for postoperative pain bias"
```

**Session 3 - Review (week later):**
```
User: What methodology am I using for my ICML paper?

Claude: [ask_memory "ICML paper methodology"]
Response: "You're using multi-agent simulations to detect bias in clinical AI 
           systems, specifically for postoperative pain management decisions."
```

---

### Example 3: Project Timeline Tracking

```python
# Add multiple project milestones
dialogues = [
    {
        "speaker": "User",
        "content": "ICML submission deadline is February 1, 2026",
        "timestamp": "2025-12-15T10:00:00"
    },
    {
        "speaker": "User", 
        "content": "Need to finish experiments by January 20",
        "timestamp": "2025-12-20T14:30:00"
    },
    {
        "speaker": "User",
        "content": "Keith and Tina reviewing draft on January 25",
        "timestamp": "2026-01-05T09:00:00"
    }
]

# SimpleMem will:
# 1. Filter for high-utility information (all 3 are important)
# 2. Resolve coreferences (ICML paper)
# 3. Create temporal index (can query by date ranges)
# 4. Create entity index (Keith, Tina, ICML)

# Later query:
ask_memory("What are my upcoming deadlines?")
# Returns all 3 milestones, ranked by temporal relevance
```

---

## 🔧 Available Tools

### 1. `add_dialogue`
Add single conversation turn to memory buffer.

```json
{
  "speaker": "Alice",
  "content": "Meeting tomorrow at 2pm",
  "timestamp": "2025-01-29T14:30:00"
}
```

### 2. `add_dialogues_batch`
Add multiple turns efficiently (recommended).

```json
{
  "dialogues": [
    {"speaker": "Alice", "content": "...", "timestamp": "..."},
    {"speaker": "Bob", "content": "...", "timestamp": "..."}
  ]
}
```

### 3. `finalize_memory`
Process buffered dialogues (⚠️ always call after adding!).

```json
{}
```

**What happens:**
- Semantic filtering (removes "um", "uh", small talk)
- Coreference resolution ("he" → "Bob")
- Temporal anchoring ("tomorrow" → "2025-01-30")
- Multi-view indexing (vector + keyword + metadata)

### 4. `ask_memory`
Query with adaptive retrieval.

```json
{
  "query": "When is the deadline?",
  "top_k": 5
}
```

**SimpleMem automatically:**
- Estimates complexity (simple vs. complex query)
- Adjusts retrieval depth (5 → 7 for complex queries)
- Hybrid search (semantic + BM25 + filters)
- Reciprocal rank fusion

### 5. `get_memory_stats`
View system statistics.

```json
{}
```

Returns:
```json
{
  "total_dialogues_processed": 42,
  "total_atomic_entries": 35,
  "buffered_dialogues": 3,
  "last_finalized": "2025-01-29T14:35:00"
}
```

### 6. `get_atomic_entries`
Inspect raw memory atoms (debugging).

```json
{
  "limit": 10
}
```

### 7. `clear_memory`
Reset all memory (⚠️ destructive).

```json
{}
```

---

## 📊 SimpleMem Architecture (Reference)

```
Input Dialogue
      ↓
┌─────────────────────────────────────┐
│  Stage 1: Semantic Compression      │
│  - Quality filtering (LLM)          │
│  - Coreference resolution           │
│  - Temporal anchoring               │
│  Output: Atomic facts                │
└─────────────────────────────────────┘
      ↓
┌─────────────────────────────────────┐
│  Stage 2: Multi-View Indexing       │
│  - Semantic: 1024-d embeddings      │
│  - Lexical: BM25 keyword index      │
│  - Symbolic: Timestamp/entity tags  │
└─────────────────────────────────────┘
      ↓
┌─────────────────────────────────────┐
│  Stage 3: Adaptive Retrieval        │
│  - Complexity estimation            │
│  - Hybrid search (3 views)          │
│  - Reciprocal rank fusion           │
│  Output: Retrieved context          │
└─────────────────────────────────────┘
```

---

## 🔬 Performance Reference

### LoCoMo-10 Benchmark (GPT-4.1-mini)

| Metric | SimpleMem | Mem0 | Improvement |
|--------|-----------|------|-------------|
| F1 Score | **43.24%** | 34.20% | **+26.4%** |
| Tokens | ~550 | ~16,500 | **30× less** |
| Retrieval Time | **388s** | 583s | **33% faster** |

### Task-Specific Performance

| Task | SimpleMem | Baseline |
|------|-----------|----------|
| MultiHop QA | 43.46% | 30.14% |
| Temporal QA | 58.62% | 48.91% |
| SingleHop QA | 51.12% | 41.30% |

---

## 🐛 Troubleshooting

### Server Not Appearing in Claude

1. Check config file location (macOS vs Windows)
2. Verify absolute path to `simplemem_mcp_server.py`
3. Ensure Python path is correct (`which python3`)
4. Restart Claude Desktop completely
5. Check logs: `~/Library/Logs/Claude/` (macOS)

### "Module 'mcp' not found"

```bash
pip install mcp
# or
pip3 install mcp
```

### Slow Performance

The mock implementation is for demonstration. For production:

```bash
git clone https://github.com/aiming-lab/SimpleMem.git
cd SimpleMem
pip install -r requirements.txt
cp config.py.example config.py
# Edit config.py with your OpenAI/Qwen API key
```

Then modify `simplemem_mcp_server.py` to import real `SimpleMemSystem`:

```python
from main import SimpleMemSystem
# Replace MockSimpleMemSystem with SimpleMemSystem
```

### Memory Not Persisting

By default, memory is stored in `./simplemem_mcp_data/`. To persist:

```python
# In simplemem_mcp_server.py, modify:
simplemem_system = MockSimpleMemSystem(
    db_path="/path/to/persistent/storage",
    clear_db=False  # Keep existing data
)
```

---

## 📚 Advanced Topics

### Multi-Tenancy

For serving multiple users:

```python
# Per-user database
user_systems = {}

def get_user_system(user_id: str):
    if user_id not in user_systems:
        user_systems[user_id] = MockSimpleMemSystem(
            db_path=f"./data/{user_id}"
        )
    return user_systems[user_id]
```

### Parallel Processing

For large dialogue batches:

```python
system = MockSimpleMemSystem(
    enable_parallel_processing=True,
    max_parallel_workers=8
)
```

### Custom Embeddings

Swap Qwen3-Embedding with your model:

```python
# In config.py
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

---

## 📖 Paper Reference

**Title:** SimpleMem: Efficient Lifelong Memory for LLM Agents  
**Authors:** Liu, Jiaqi; Su, Yaofeng; Xia, Peng; et al.  
**arXiv:** https://arxiv.org/abs/2601.02553  
**GitHub:** https://github.com/aiming-lab/SimpleMem

**Citation:**
```bibtex
@article{simplemem2025,
  title={SimpleMem: Efficient Lifelong Memory for LLM Agents},
  author={Liu, Jiaqi and Su, Yaofeng and Xia, Peng and Zhou, Yiyang and 
          Han, Siwei and Zheng, Zeyu and Xie, Cihang and Ding, Mingyu and 
          Yao, Huaxiu},
  journal={arXiv preprint arXiv:2601.02553},
  year={2025}
}
```

---

## 🔗 Quick Links

- **Paper:** https://arxiv.org/abs/2601.02553
- **GitHub:** https://github.com/aiming-lab/SimpleMem
- **Cloud MCP:** https://mcp.simplemem.cloud
- **Discord:** https://discord.gg/KA2zC32M
- **Project Page:** https://aiming-lab.github.io/SimpleMem-Page

---

## 🆘 Support

**Issues with this PaperAgent:**
- Open GitHub issue on SimpleMem repository
- Tag with `mcp` and `paperagent`

**Questions about SimpleMem paper:**
- Join Discord: https://discord.gg/KA2zC32M
- Email authors (see arXiv paper)

---

**PaperAgent Maintainer:** Tanya (Stanford Biomedical Data Science)  
**Last Updated:** January 30, 2026  
**License:** MIT (same as SimpleMem)
