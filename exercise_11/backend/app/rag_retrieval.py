"""
RAG Retrieval Helper
Retrieves relevant knowledge base entries for user queries and provides citations.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
from .observability import get_tracer


class RAGRetrieval:
    """Retrieval helper for RAG knowledge base"""
    
    def __init__(self, index_path: Optional[Path] = None, retrieval_index_path: Optional[Path] = None):
        """
        Initialize RAG retrieval system.
        
        Args:
            index_path: Path to rag/index.json
            retrieval_index_path: Path to rag/retrieval_index.json (created by ingest.py)
        """
        if index_path is None:
            project_root = Path(__file__).parent.parent.parent
            index_path = project_root / "rag" / "index.json"
        
        if retrieval_index_path is None:
            project_root = Path(__file__).parent.parent.parent
            retrieval_index_path = project_root / "rag" / "retrieval_index.json"
        
        self.index_path = index_path
        self.retrieval_index_path = retrieval_index_path
        
        # Load data
        self.kb_data = self._load_knowledge_base()
        self.retrieval_index = self._load_retrieval_index()
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load the knowledge base"""
        try:
            with open(self.index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Knowledge base not found: {self.index_path}. "
                "Run rag/ingest.py to create the index."
            )
    
    def _load_retrieval_index(self) -> Dict[str, Any]:
        """Load the retrieval index"""
        try:
            with open(self.retrieval_index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback: create index on the fly if not found
            print(f"Warning: Retrieval index not found at {self.retrieval_index_path}")
            print("Creating index on the fly...")
            return self._create_index_on_fly()
    
    def _create_index_on_fly(self) -> Dict[str, Any]:
        """Create a simple index on the fly if retrieval_index.json doesn't exist"""
        index = {
            "keyword_map": {},
            "entry_map": {},
            "category_map": {}
        }
        
        for entry in self.kb_data.get("knowledge_base", []):
            entry_id = entry["id"]
            index["entry_map"][entry_id] = entry
            
            # Index keywords
            for keyword in entry.get("keywords", []):
                keyword_lower = keyword.lower()
                if keyword_lower not in index["keyword_map"]:
                    index["keyword_map"][keyword_lower] = []
                if entry_id not in index["keyword_map"][keyword_lower]:
                    index["keyword_map"][keyword_lower].append(entry_id)
            
            # Index tags
            for tag in entry.get("tags", []):
                tag_lower = tag.lower()
                if tag_lower not in index["keyword_map"]:
                    index["keyword_map"][tag_lower] = []
                if entry_id not in index["keyword_map"][tag_lower]:
                    index["keyword_map"][tag_lower].append(entry_id)
            
            # Index category
            category = entry.get("category", "uncategorized")
            if category not in index["category_map"]:
                index["category_map"][category] = []
            if entry_id not in index["category_map"][category]:
                index["category_map"][category].append(entry_id)
        
        return index
    
    def retrieve(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant knowledge base entries for a query.
        
        Args:
            query: User query string
            max_results: Maximum number of results to return
        
        Returns:
            List of relevant knowledge base entries with citations
        """
        tracer = get_tracer()
        start_time = time.time()
        
        with tracer.start_as_current_span("retrieval.retrieve") as span:
            span.set_attribute("retrieval.query_length", len(query))
            span.set_attribute("retrieval.max_results", max_results)
            
            query_lower = query.lower()
            
            # Extract keywords from query
            words = re.findall(r'\b\w+\b', query_lower)
            
            # Score entries based on keyword matches
            entry_scores = {}
            entry_ids_seen = set()
            
            for word in words:
                # Skip common stop words
                if word in ['a', 'an', 'the', 'is', 'are', 'was', 'were', 'how', 'what', 'when', 'where', 'why', 'can', 'could', 'should', 'would', 'my', 'child', 'children']:
                    continue
                
                # Check keyword matches
                if word in self.retrieval_index["keyword_map"]:
                    for entry_id in self.retrieval_index["keyword_map"][word]:
                        if entry_id not in entry_scores:
                            entry_scores[entry_id] = 0
                        entry_scores[entry_id] += 2  # Keyword match is worth 2 points
                
                # Check partial matches in content
                for entry_id, entry in self.retrieval_index["entry_map"].items():
                    content_lower = entry.get("content", "").lower()
                    if word in content_lower:
                        if entry_id not in entry_scores:
                            entry_scores[entry_id] = 0
                        entry_scores[entry_id] += 1  # Content match is worth 1 point
            
            # Sort by score (highest first)
            sorted_entries = sorted(entry_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Get top results
            results = []
            for entry_id, score in sorted_entries[:max_results]:
                entry = self.retrieval_index["entry_map"].get(entry_id)
                if entry:
                    # Add citation info
                    entry_with_citation = {
                        **entry,
                        "citation": {
                            "id": entry_id,
                            "title": entry.get("title"),
                            "source": entry.get("source"),
                            "source_url": entry.get("source_url"),
                            "category": entry.get("category")
                        },
                        "relevance_score": score
                    }
                    results.append(entry_with_citation)
            
            # If no matches found, return a general entry
            if not results:
                # Return first entry as fallback
                first_entry = list(self.retrieval_index["entry_map"].values())[0]
                if first_entry:
                    results.append({
                        **first_entry,
                        "citation": {
                            "id": first_entry["id"],
                            "title": first_entry.get("title"),
                            "source": first_entry.get("source"),
                            "source_url": first_entry.get("source_url"),
                            "category": first_entry.get("category")
                        },
                        "relevance_score": 0
                    })
            
            # Set span attributes for observability
            latency_ms = (time.time() - start_time) * 1000
            top_score = results[0].get("relevance_score", 0) if results else 0
            span.set_attribute("retrieval.latency_ms", latency_ms)
            span.set_attribute("retrieval.results_count", len(results))
            span.set_attribute("retrieval.top_relevance_score", top_score)
            span.set_attribute("retrieval.is_fallback", top_score == 0)
            
            return results
    
    def format_citation(self, citation: Dict[str, Any]) -> str:
        """
        Format a citation for display.
        
        Returns:
            Formatted citation string
        """
        source = citation.get("source", "Knowledge Base")
        source_url = citation.get("source_url", "")
        
        if source_url:
            return f"{source}"
        return source


# Global retrieval instance
_retrieval_instance: Optional[RAGRetrieval] = None


def get_rag_retrieval() -> RAGRetrieval:
    """Get or create the global RAG retrieval instance"""
    global _retrieval_instance
    if _retrieval_instance is None:
        _retrieval_instance = RAGRetrieval()
    return _retrieval_instance


def retrieve_knowledge(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Convenience function to retrieve knowledge base entries.
    
    Args:
        query: User query
        max_results: Maximum number of results
    
    Returns:
        List of relevant entries with citations
    """
    retrieval = get_rag_retrieval()
    return retrieval.retrieve(query, max_results)

