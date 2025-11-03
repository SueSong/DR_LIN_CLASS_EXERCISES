"""
Lite Mode Module
Provides simplified, cost-effective responses when over budget.
"""

from typing import Dict, List, Optional


def generate_lite_mode_response(
    user_text: str,
    retrieved_knowledge: Optional[List[Dict]] = None
) -> str:
    """
    Generate a simplified "lite mode" response when budget is exceeded.
    
    Args:
        user_text: User's question
        retrieved_knowledge: Retrieved RAG content (optional)
        
    Returns:
        Simplified response text
    """
    # Lite mode uses shorter, more direct responses
    # Instead of full detailed advice, provide concise guidance
    
    # Extract main topic from user text (first few words)
    topic = ' '.join(user_text.split()[:5])
    
    base_response = (
        f"Brief guidance on {topic}:\n\n"
    )
    
    if retrieved_knowledge and len(retrieved_knowledge) > 0:
        # Use first result but summarize briefly
        top_entry = retrieved_knowledge[0]
        content = top_entry.get("content", "")
        
        # Extract key points (first 2 sentences only) and limit to 120 characters max
        sentences = content.split('.')
        key_points = '. '.join(sentences[:2]) + '.' if len(sentences) >= 2 else content[:120]
        
        # Ensure maximum length for lite mode (make it noticeably shorter)
        if len(key_points) > 120:
            key_points = key_points[:117] + "..."
        
        response = base_response + key_points
        
        # Add citation if available (shortened)
        citation = top_entry.get("citation", {})
        if citation.get("title"):
            # Only show title, not full source
            title = citation.get("title", "")[:50]  # Limit citation title length
            response += f"\n\n📚 {title}"
    else:
        # Generic helpful response
        response = base_response + (
            "I'm currently operating in a limited capacity mode. "
            "For more detailed guidance, please try again later. "
            "You can also consult parenting resources and child development experts for comprehensive support."
        )
    
    # Add budget notice (shorter for lite mode)
    response += (
        "\n\n⚠️ Lite mode: Daily budget exceeded. Response simplified."
    )
    
    return response


def get_lite_mode_notice() -> Dict[str, str]:
    """
    Get notice message for lite mode responses.
    
    Returns:
        Dictionary with notice information
    """
    return {
        "type": "budget_limit",
        "message": "Daily budget exceeded. Using lite mode.",
        "mode": "lite"
    }

