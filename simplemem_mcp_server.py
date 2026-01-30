#!/usr/bin/env python3
"""
SimpleMem MCP Server - PaperAgent Implementation
================================================

A Model Context Protocol (MCP) server that provides SimpleMem's semantic 
lossless compression memory system as a service for AI assistants.

Features:
- Semantic structured compression of dialogues
- Multi-view hybrid retrieval (semantic + lexical + symbolic)
- Adaptive query-aware search
- Persistent memory storage with LanceDB

Author: Tanya (Stanford Biomedical Data Science)
Based on: SimpleMem by Liu et al. (2025)
License: MIT
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# MCP Server framework
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
except ImportError:
    print("ERROR: mcp package not found. Install with: pip install mcp")
    exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("simplemem-mcp")

# Mock SimpleMem implementation for demonstration
# In production, this would import from the actual SimpleMem package
class MockSimpleMemSystem:
    """
    Mock SimpleMem system for demonstration.
    In production, replace with actual SimpleMem implementation.
    """
    def __init__(self, db_path: str = "./lancedb_data", clear_db: bool = False):
        self.db_path = db_path
        self.dialogue_buffer = []
        self.memory_entries = []
        self.metadata = {
            "total_dialogues": 0,
            "total_atoms": 0,
            "last_finalized": None
        }
        logger.info(f"Initialized MockSimpleMemSystem with db_path={db_path}")
    
    def add_dialogue(self, speaker: str, content: str, timestamp: str) -> Dict[str, Any]:
        """Add a single dialogue to the buffer"""
        dialogue = {
            "speaker": speaker,
            "content": content,
            "timestamp": timestamp
        }
        self.dialogue_buffer.append(dialogue)
        self.metadata["total_dialogues"] += 1
        logger.info(f"Added dialogue from {speaker}: {content[:50]}...")
        return {"status": "buffered", "dialogue_id": len(self.dialogue_buffer) - 1}
    
    def add_dialogues_batch(self, dialogues: List[Dict[str, str]]) -> Dict[str, Any]:
        """Add multiple dialogues efficiently"""
        for d in dialogues:
            self.add_dialogue(d["speaker"], d["content"], d["timestamp"])
        return {
            "status": "buffered",
            "count": len(dialogues),
            "total_buffered": len(self.dialogue_buffer)
        }
    
    def finalize(self) -> Dict[str, Any]:
        """
        Process buffered dialogues into atomic memory entries.
        This is where SimpleMem's semantic compression happens.
        """
        if not self.dialogue_buffer:
            return {"status": "no_dialogues_to_process"}
        
        # Mock processing - in reality this would:
        # 1. Apply semantic filtering
        # 2. Extract atomic facts with coreference resolution
        # 3. Create multi-view indexes (semantic + lexical + symbolic)
        num_processed = len(self.dialogue_buffer)
        
        # Simulate atomic fact extraction
        for dialogue in self.dialogue_buffer:
            atomic_fact = {
                "speaker": dialogue["speaker"],
                "fact": dialogue["content"],  # Would be transformed
                "timestamp": dialogue["timestamp"],
                "embedding_id": f"emb_{len(self.memory_entries)}"
            }
            self.memory_entries.append(atomic_fact)
            self.metadata["total_atoms"] += 1
        
        self.dialogue_buffer = []
        self.metadata["last_finalized"] = datetime.now().isoformat()
        
        logger.info(f"Finalized {num_processed} dialogues into atomic entries")
        return {
            "status": "success",
            "processed": num_processed,
            "total_atoms": self.metadata["total_atoms"]
        }
    
    def ask(self, query: str, top_k: int = 5) -> str:
        """
        Query memory with adaptive retrieval.
        In production, this would:
        1. Estimate query complexity
        2. Perform hybrid retrieval (semantic + lexical + symbolic)
        3. Apply reciprocal rank fusion
        4. Construct context efficiently
        """
        logger.info(f"Query received: {query}")
        
        if not self.memory_entries:
            return "No memories stored yet. Please add dialogues and finalize."
        
        # Mock retrieval - would use vector similarity + BM25 + metadata filters
        relevant_entries = self.memory_entries[:min(top_k, len(self.memory_entries))]
        
        # Mock answer generation
        context = "\n".join([
            f"[{e['timestamp']}] {e['speaker']}: {e['fact']}"
            for e in relevant_entries
        ])
        
        answer = f"""Based on memory retrieval:

Retrieved Memories:
{context}

Answer: [This would be generated by LLM based on retrieved context]
For query: "{query}"

Note: This is a mock implementation. Production SimpleMem would use:
- Semantic vector search (1024-d embeddings)
- BM25 keyword matching
- Temporal/entity filtering
- Complexity-aware retrieval depth
"""
        return answer
    
    def get_atomic_entries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve raw atomic memory entries"""
        return self.memory_entries[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            "total_dialogues_processed": self.metadata["total_dialogues"],
            "total_atomic_entries": self.metadata["total_atoms"],
            "buffered_dialogues": len(self.dialogue_buffer),
            "last_finalized": self.metadata["last_finalized"],
            "database_path": self.db_path
        }
    
    def clear(self) -> Dict[str, Any]:
        """Clear all memory"""
        self.dialogue_buffer = []
        self.memory_entries = []
        self.metadata = {
            "total_dialogues": 0,
            "total_atoms": 0,
            "last_finalized": None
        }
        logger.warning("Memory cleared!")
        return {"status": "cleared"}


# Initialize global SimpleMem instance
# In production, this would handle multi-tenancy with user-specific databases
simplemem_system = MockSimpleMemSystem(db_path="./simplemem_mcp_data")

# Create MCP server
app = Server("simplemem-paperagent")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """
    Define available MCP tools for SimpleMem.
    Each tool corresponds to a SimpleMem capability.
    """
    return [
        Tool(
            name="add_dialogue",
            description="""
            Add a single dialogue turn to SimpleMem's memory buffer.
            
            SimpleMem will apply semantic filtering and coreference resolution 
            when you call finalize_memory.
            
            Parameters:
            - speaker: Name of the person speaking
            - content: What they said (can include relative references like "tomorrow")
            - timestamp: ISO format datetime (e.g., "2025-01-20T14:30:00")
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "speaker": {"type": "string", "description": "Speaker name"},
                    "content": {"type": "string", "description": "Dialogue content"},
                    "timestamp": {"type": "string", "description": "ISO timestamp"}
                },
                "required": ["speaker", "content", "timestamp"]
            }
        ),
        Tool(
            name="add_dialogues_batch",
            description="""
            Add multiple dialogue turns efficiently (recommended for >1 turn).
            
            This is more efficient than calling add_dialogue multiple times.
            SimpleMem processes dialogues in windows of 40 for optimal performance.
            
            Parameters:
            - dialogues: Array of {speaker, content, timestamp} objects
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "dialogues": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "speaker": {"type": "string"},
                                "content": {"type": "string"},
                                "timestamp": {"type": "string"}
                            },
                            "required": ["speaker", "content", "timestamp"]
                        }
                    }
                },
                "required": ["dialogues"]
            }
        ),
        Tool(
            name="finalize_memory",
            description="""
            Process buffered dialogues into atomic memory entries.
            
            ⚠️ IMPORTANT: Always call this after adding dialogues!
            
            This triggers SimpleMem's semantic compression pipeline:
            1. Semantic filtering (removes low-utility content)
            2. Atomic fact extraction (resolves coreferences)
            3. Multi-view indexing (semantic + lexical + symbolic)
            
            SimpleMem uses windowed processing (40 dialogues/window),
            so call this to ensure all dialogues are processed.
            """,
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="ask_memory",
            description="""
            Query SimpleMem with adaptive complexity-aware retrieval.
            
            SimpleMem automatically:
            - Estimates query complexity
            - Adjusts retrieval depth (k_dyn = k_base × (1 + δ × C_q))
            - Performs hybrid search (semantic + lexical + symbolic)
            - Merges results with reciprocal rank fusion
            
            Returns answer based on retrieved atomic facts.
            
            Parameters:
            - query: Natural language question
            - top_k: Base retrieval depth (default: 5, adjusted by complexity)
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Question to ask"},
                    "top_k": {"type": "integer", "description": "Retrieval depth", "default": 5}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_memory_stats",
            description="""
            Get SimpleMem system statistics and metadata.
            
            Returns:
            - Total dialogues processed
            - Total atomic entries stored
            - Buffered dialogues awaiting finalization
            - Last finalization timestamp
            - Database path
            """,
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_atomic_entries",
            description="""
            View raw atomic memory entries (for debugging/inspection).
            
            Returns the actual atomic facts stored in SimpleMem's database.
            Each entry includes:
            - Resolved coreferences
            - Absolute timestamps
            - Semantic embeddings
            
            Parameters:
            - limit: Maximum number of entries to return (default: 10)
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max entries", "default": 10}
                },
                "required": []
            }
        ),
        Tool(
            name="clear_memory",
            description="""
            Clear all memory from SimpleMem (⚠️ destructive operation).
            
            Use with caution! This removes:
            - All buffered dialogues
            - All atomic memory entries
            - All indexes
            
            Useful for starting fresh or testing.
            """,
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """
    Handle MCP tool calls.
    Routes requests to appropriate SimpleMem methods.
    """
    try:
        result = None
        
        if name == "add_dialogue":
            result = simplemem_system.add_dialogue(
                speaker=arguments["speaker"],
                content=arguments["content"],
                timestamp=arguments["timestamp"]
            )
        
        elif name == "add_dialogues_batch":
            result = simplemem_system.add_dialogues_batch(
                dialogues=arguments["dialogues"]
            )
        
        elif name == "finalize_memory":
            result = simplemem_system.finalize()
        
        elif name == "ask_memory":
            query = arguments["query"]
            top_k = arguments.get("top_k", 5)
            answer = simplemem_system.ask(query, top_k)
            result = {"answer": answer}
        
        elif name == "get_memory_stats":
            result = simplemem_system.get_stats()
        
        elif name == "get_atomic_entries":
            limit = arguments.get("limit", 10)
            entries = simplemem_system.get_atomic_entries(limit)
            result = {"entries": entries, "count": len(entries)}
        
        elif name == "clear_memory":
            result = simplemem_system.clear()
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
        
        # Format response
        response_text = json.dumps(result, indent=2)
        return [TextContent(type="text", text=response_text)]
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """
    Start the SimpleMem MCP server.
    
    This server communicates via STDIO (JSON-RPC 2.0 over stdin/stdout).
    Designed to work with Claude Desktop, Cursor, and other MCP clients.
    """
    logger.info("Starting SimpleMem PaperAgent MCP Server...")
    logger.info("Based on: SimpleMem (Liu et al., 2025)")
    logger.info("GitHub: https://github.com/aiming-lab/SimpleMem")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
