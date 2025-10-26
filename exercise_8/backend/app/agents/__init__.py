"""
Multi-Agent Orchestration Framework for Exercise 8

This module provides the core classes for building multi-agent systems:
- Agent: Individual agent with specific capabilities
- Team: Collection of agents working together
- Coordinator: Orchestrates agent execution and manages shared state (Blackboard)
"""

from .agent import Agent
from .team import Team
from .coordinator import Coordinator

__all__ = ["Agent", "Team", "Coordinator"]
