"""
RAG Ingestion Script
Processes and indexes parenting knowledge base documents for retrieval.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
import hashlib


def load_knowledge_base(index_path: Path) -> Dict[str, Any]:
    """Load the knowledge base from index.json"""
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_retrieval_index(kb_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a searchable index from the knowledge base.
    This creates keyword-based indexing for fast retrieval.
    """
    index = {
        "keyword_map": {},  # keyword -> [entry_ids]
        "entry_map": {},    # entry_id -> full_entry
        "category_map": {}  # category -> [entry_ids]
    }
    
    for entry in kb_data.get("knowledge_base", []):
        entry_id = entry["id"]
        
        # Store full entry
        index["entry_map"][entry_id] = entry
        
        # Index by keywords
        for keyword in entry.get("keywords", []):
            keyword_lower = keyword.lower()
            if keyword_lower not in index["keyword_map"]:
                index["keyword_map"][keyword_lower] = []
            if entry_id not in index["keyword_map"][keyword_lower]:
                index["keyword_map"][keyword_lower].append(entry_id)
        
        # Index by tags
        for tag in entry.get("tags", []):
            tag_lower = tag.lower()
            if tag_lower not in index["keyword_map"]:
                index["keyword_map"][tag_lower] = []
            if entry_id not in index["keyword_map"][tag_lower]:
                index["keyword_map"][tag_lower].append(entry_id)
        
        # Index by category
        category = entry.get("category", "uncategorized")
        if category not in index["category_map"]:
            index["category_map"][category] = []
        if entry_id not in index["category_map"][category]:
            index["category_map"][category].append(entry_id)
    
    return index


def save_retrieval_index(index: Dict[str, Any], output_path: Path):
    """Save the retrieval index to a JSON file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


def main():
    """Main ingestion function"""
    # Get paths
    script_dir = Path(__file__).parent
    index_path = script_dir / "index.json"
    output_path = script_dir / "retrieval_index.json"
    
    print(f"📚 Loading knowledge base from {index_path}")
    
    # Load knowledge base
    kb_data = load_knowledge_base(index_path)
    total_entries = len(kb_data.get("knowledge_base", []))
    print(f"✅ Loaded {total_entries} knowledge base entries")
    
    # Create retrieval index
    print("🔍 Creating retrieval index...")
    retrieval_index = create_retrieval_index(kb_data)
    
    # Calculate statistics
    total_keywords = len(retrieval_index["keyword_map"])
    total_categories = len(retrieval_index["category_map"])
    
    print(f"✅ Indexed {total_keywords} unique keywords/tags")
    print(f"✅ Indexed {total_categories} categories")
    print(f"✅ Mapped {len(retrieval_index['entry_map'])} entries")
    
    # Save retrieval index
    print(f"💾 Saving retrieval index to {output_path}")
    save_retrieval_index(retrieval_index, output_path)
    
    print("🎉 Ingestion complete!")
    print(f"\nIndex Summary:")
    print(f"  - Knowledge entries: {total_entries}")
    print(f"  - Searchable keywords: {total_keywords}")
    print(f"  - Categories: {total_categories}")
    print(f"  - Output file: {output_path}")


if __name__ == "__main__":
    main()

