# SimpleMem PaperAgent Documentation

## 📄 Paper Information

**Title:** SimpleMem: Efficient Lifelong Memory for LLM Agents  
**Authors:** Liu, Jiaqi; Su, Yaofeng; Xia, Peng; Zhou, Yiyang; Han, Siwei; Zheng, Zeyu; Xie, Cihang; Ding, Mingyu; Yao, Huaxiu  
**Published:** January 2025  
**arXiv:** https://arxiv.org/abs/2601.02553  
**GitHub:** https://github.com/aiming-lab/SimpleMem  
**License:** MIT

---

## 🎯 Problem Statement

Large Language Models (LLMs) struggle with **long-term memory management** in agent applications. Existing approaches face two major challenges:

1. **Context Window Limitations**: Cannot store indefinite conversation history
2. **Efficiency Trade-offs**: Either accumulate redundant context (high token cost) or use expensive iterative reasoning loops

**Key Challenge:** How to maintain high-quality, long-term memory while minimizing computational overhead?

---

## 💡 Core Innovation: Semantic Lossless Compression

SimpleMem introduces a **three-stage pipeline** based on semantic lossless compression:

### Stage 1: Semantic Structured Compression
- **Goal:** Transform raw dialogue into atomic, self-contained facts
- **Method:** Entropy-based filtering + de-linearization
- **Output:** Context-independent memory units with resolved coreferences

**Example Transformation:**
```
❌ Input:  "He'll meet Bob tomorrow at 2pm"  [relative, ambiguous]
✅ Output: "Alice will meet Bob at Starbucks on 2025-11-16T14:00:00"  [absolute, atomic]
```

### Stage 2: Structured Indexing (Asynchronous Memory Consolidation)
- **Goal:** Organize atomic facts into higher-order molecular insights
- **Method:** Multi-view indexing across three dimensions:
  - **Semantic Layer:** Dense vector embeddings (1024-d) for conceptual similarity
  - **Lexical Layer:** BM25-style sparse keyword index for exact matching
  - **Symbolic Layer:** Structured metadata (timestamps, entities, persons)

### Stage 3: Adaptive Query-Aware Retrieval
- **Goal:** Dynamically adjust retrieval depth based on query complexity
- **Method:** Complexity estimation → adaptive token allocation
- **Formula:** k_dyn = ⌊k_base × (1 + δ × C_q)⌋

**Complexity-Aware Scaling:**
- **Low Complexity:** ~100 tokens (minimal molecular headers)
- **High Complexity:** ~1000 tokens (detailed atomic contexts)

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     SimpleMem Pipeline                        │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐      ┌─────────────┐      ┌──────────────┐ │
│  │   Stage 1   │  →   │   Stage 2   │  →   │   Stage 3    │ │
│  │  Semantic   │      │ Structured  │      │  Adaptive    │ │
│  │ Compression │      │  Indexing   │      │  Retrieval   │ │
│  └─────────────┘      └─────────────┘      └──────────────┘ │
│        ↓                     ↓                     ↓         │
│   Atomic Facts        Multi-View Index      Complexity-     │
│   (resolved refs)    (Sem+Lex+Sym)         Aware Search    │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Input:** Raw dialogue stream with speaker, content, timestamp
2. **Windowed Processing:** Groups of 40 dialogues processed in parallel
3. **Semantic Filtering:** LLM-based qualitative assessment removes low-utility content
4. **Atomic Encoding:** Coreference resolution + temporal anchoring
5. **Memory Storage:** LanceDB vector database with hybrid indexing
6. **Query Processing:** Intent inference → retrieval planning → context construction
7. **Output:** Retrieved memories ranked by relevance

---

## 📊 Performance Metrics

### LoCoMo-10 Benchmark Results (GPT-4.1-mini)

| Metric | SimpleMem | Mem0 | A-Mem | LightMem |
|--------|-----------|------|-------|----------|
| **Average F1** | **43.24%** | 34.20% | 32.58% | 24.63% |
| **Construction Time** | 92.6s | 1350.9s | 5140.5s | 97.8s |
| **Retrieval Time** | **388.3s** | 583.4s | 796.7s | 577.1s |
| **Total Time** | **480.9s** | 1934.3s | 5937.2s | 675.9s |
| **Token Cost** | ~550 | ~16,500 | ~25,000 | ~800 |

### Key Improvements

- **+26.4% F1 vs. Mem0** (best existing baseline)
- **+75.6% F1 vs. LightMem** (fastest baseline)
- **30× fewer tokens** than full-context methods
- **12.5× faster** end-to-end than A-Mem

### Task-Specific Performance

| Task Type | SimpleMem | Improvement |
|-----------|-----------|-------------|
| MultiHop | 43.46% | +43.8% vs. Mem0 |
| Temporal | 58.62% | +19.9% vs. Mem0 |
| SingleHop | 51.12% | +23.8% vs. Mem0 |

---

## 🔧 Technical Implementation

### Core Components

#### 1. Memory Manager (`core/memory_manager.py`)
- Dialogue buffer management
- Windowed processing (default: 40 dialogues)
- Parallel processing support
- Memory consolidation triggers

#### 2. Semantic Compressor (`core/compressor.py`)
- LLM-based quality filtering
- Coreference resolution
- Temporal anchoring
- Atomic fact extraction

#### 3. Hybrid Retriever (`core/retriever.py`)
- **Semantic search:** Vector similarity (cosine)
- **Lexical search:** BM25 keyword matching
- **Symbolic filter:** Metadata constraints
- Reciprocal Rank Fusion (RRF) for result merging

#### 4. Database Layer (`database/lancedb_manager.py`)
- LanceDB vector store
- 1024-dimensional embeddings (Qwen3-Embedding-0.6B)
- Efficient columnar storage
- Multi-tenant support (via table prefixes)

### Key Algorithms

#### Windowed Memory Processing
```python
def process_window(dialogues: List[Dialogue]) -> List[AtomicFact]:
    # Stage 1: Filter low-utility content
    filtered = semantic_filter(dialogues)
    
    # Stage 1: Extract atomic facts
    atomic_facts = []
    for dialogue in filtered:
        facts = extract_atoms(dialogue)
        atomic_facts.extend(facts)
    
    # Stage 2: Index facts
    for fact in atomic_facts:
        index_fact(fact)  # Semantic + Lexical + Symbolic
    
    return atomic_facts
```

#### Complexity-Aware Retrieval
```python
def adaptive_retrieve(query: str, k_base: int = 5) -> List[Memory]:
    # Estimate query complexity
    complexity = estimate_complexity(query)
    
    # Adjust retrieval depth
    k_dynamic = int(k_base * (1 + 0.5 * complexity))
    
    # Multi-view retrieval
    semantic_results = semantic_search(query, k=k_dynamic)
    lexical_results = keyword_search(query, k=k_dynamic)
    
    # Merge with RRF
    merged = reciprocal_rank_fusion([semantic_results, lexical_results])
    
    return merged[:k_dynamic]
```

---

## 🌐 MCP Server Integration

SimpleMem provides a **Model Context Protocol (MCP) server** for seamless integration with AI assistants.

### Architecture

```
┌─────────────────────────┐
│   MCP Client            │
│   (Claude, Cursor)      │
└───────────┬─────────────┘
            │ JSON-RPC over HTTP/STDIO
            ▼
┌─────────────────────────────────┐
│   SimpleMem MCP Server (Node)   │
│   - Tool handlers               │
│   - Resource providers          │
│   - Input validation (Zod)     │
└───────────┬─────────────────────┘
            │ spawn Python process
            ▼
┌─────────────────────────────────┐
│   SimpleMem Core (Python)       │
│   - Semantic compression        │
│   - Hybrid retrieval            │
│   - LanceDB vector store        │
└─────────────────────────────────┘
```

### Available Tools

1. **add_dialogue** - Add single conversation turn
2. **add_dialogues_batch** - Add multiple turns efficiently
3. **finalize_memory** - Process buffered dialogues
4. **ask_memory** - Query with adaptive retrieval
5. **get_atomic_entries** - View raw memory atoms
6. **get_molecular_summaries** - View consolidated insights
7. **clear_memory** - Reset database

### Deployment Options

#### Option 1: Cloud Service (Recommended)
- **URL:** https://mcp.simplemem.cloud/mcp
- **Auth:** Bearer token (register at https://mcp.simplemem.cloud)
- **Features:** Multi-tenant isolation, production optimizations

#### Option 2: Self-Hosted (Local)
- **Transport:** STDIO (for Claude Desktop/Cursor)
- **Requirements:** Node.js, Python 3.10+, SimpleMem installed
- **Config:** `claude_desktop_config.json`

---

## 📝 Usage Examples

### Basic Python Usage

```python
from main import SimpleMemSystem

# Initialize system
system = SimpleMemSystem(clear_db=True)

# Add conversations
system.add_dialogue(
    speaker="Alice",
    content="Bob, let's meet at Starbucks tomorrow at 2pm",
    timestamp="2025-11-15T14:30:00"
)
system.add_dialogue(
    speaker="Bob",
    content="Sure, I'll bring the market analysis report",
    timestamp="2025-11-15T14:31:00"
)

# Finalize atomic encoding
system.finalize()

# Query memory
answer = system.ask("When and where will Alice and Bob meet?")
print(answer)
# Output: "16 November 2025 at 2:00 PM at Starbucks"
```

### MCP Client Usage (Claude Desktop)

**Configuration (`claude_desktop_config.json`):**
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

**Example Interaction:**
```
User: Remember this conversation. Alice said: "Bob, let's meet at Starbucks 
      tomorrow at 2pm." Bob replied: "Sure, I'll bring the report."

Claude: [Uses add_dialogues_batch tool]
        I've stored that conversation in memory.

User: When and where will they meet?

Claude: [Uses ask_memory tool]
        Alice and Bob will meet at Starbucks on November 16, 2025 at 2:00 PM.
```

---

## 🔬 Evaluation & Benchmarking

### Running LoCoMo Benchmark

```bash
# Full benchmark (10 samples)
python test_locomo10.py

# Subset (5 samples)
python test_locomo10.py --num-samples 5

# Custom output
python test_locomo10.py --result-file my_results.json
```

### Metrics Computed

- **F1 Score:** Harmonic mean of precision and recall
- **Construction Time:** Time to encode dialogues into memory
- **Retrieval Time:** Time to answer queries
- **Token Cost:** Total tokens used in retrieval context

---

## 🎓 Key Takeaways

### Strengths

1. **Semantic Lossless Compression** - No information loss while reducing tokens by 30×
2. **Multi-View Indexing** - Robust retrieval across semantic, lexical, symbolic dimensions
3. **Adaptive Retrieval** - Query complexity drives resource allocation
4. **Production-Ready** - MCP integration, multi-tenant support, cloud deployment
5. **State-of-the-Art Performance** - 43.24% F1 on LoCoMo-10 benchmark

### Limitations

1. **Latency:** Windowed processing introduces slight delay (mitigated by parallel mode)
2. **LLM Dependency:** Requires quality LLM for semantic filtering and QA
3. **Embedding Model:** Performance tied to Qwen3-Embedding-0.6B quality
4. **Configuration Complexity:** Multiple hyperparameters to tune

### Best For

- ✅ Long-running AI agents with extended conversation history
- ✅ Personal assistants requiring multi-session memory
- ✅ Customer service bots with user interaction history
- ✅ Research assistants tracking project knowledge over time

### Not Ideal For

- ❌ Single-turn QA (simpler retrieval sufficient)
- ❌ Extremely low-latency applications (<100ms requirement)
- ❌ Purely symbolic/structured data (traditional DB better)

---

## 📚 Related Work Comparison

| System | Approach | F1 Score | Token Cost | Latency |
|--------|----------|----------|------------|---------|
| **SimpleMem** | Semantic compression | **43.24%** | ~550 | **Fast** |
| Mem0 | Graph-based | 34.20% | ~16,500 | Medium |
| A-Mem | Iterative refinement | 32.58% | ~25,000 | Slow |
| LightMem | Sparse indexing | 24.63% | ~800 | **Fast** |
| MemGPT | Virtual context | 28.10% | ~8,000 | Medium |

**SimpleMem** occupies the optimal **top-left corner** (high performance, low cost).

---

## 🔗 Resources

- **Paper:** https://arxiv.org/abs/2601.02553
- **GitHub:** https://github.com/aiming-lab/SimpleMem
- **MCP Server:** https://mcp.simplemem.cloud
- **Discord:** https://discord.gg/KA2zC32M
- **Project Page:** https://aiming-lab.github.io/SimpleMem-Page
- **LoCoMo Benchmark:** https://github.com/snap-research/locomo

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

**Last Updated:** January 2026  
**PaperAgent Version:** 1.0  
**Maintainer:** Tanya (Stanford Biomedical Data Science)
