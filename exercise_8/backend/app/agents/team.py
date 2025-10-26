"""
Team Class

A Team is a collection of agents that work together on a common goal.
Teams can be organized in different patterns:
- Manager-Worker: One manager delegates to multiple workers
- Pipeline: Agents execute in sequence
- Parallel: Agents execute simultaneously
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from .agent import Agent, AgentStatus, AgentResult


class TeamPattern(str, Enum):
    """Team execution patterns"""
    SEQUENTIAL = "sequential"  # Agents execute one after another
    PARALLEL = "parallel"      # Agents execute simultaneously
    MANAGER_WORKER = "manager_worker"  # Manager delegates to workers
    PIPELINE = "pipeline"      # Output of one agent feeds into next


class Team:
    """
    A Team coordinates multiple agents working together.
    
    Example:
        # Create a document review team
        team = Team(
            name="document_review_team",
            pattern=TeamPattern.SEQUENTIAL
        )
        
        # Add agents
        team.add_agent(ParserAgent())
        team.add_agent(RiskAnalyzerAgent())
        team.add_agent(RedlineGeneratorAgent())
        
        # Execute team
        result = team.execute(task, blackboard)
    """
    
    def __init__(
        self,
        name: str,
        pattern: TeamPattern = TeamPattern.SEQUENTIAL,
        description: Optional[str] = None
    ):
        """
        Initialize a Team.
        
        Args:
            name: Unique identifier for this team
            pattern: Execution pattern (sequential, parallel, etc.)
            description: Optional description of team purpose
        """
        self.name = name
        self.pattern = pattern
        self.description = description or f"Team: {name}"
        self.agents: List[Agent] = []
        self.execution_history: List[Dict[str, Any]] = []
    
    def add_agent(self, agent: Agent) -> None:
        """
        Add an agent to the team.
        
        Args:
            agent: Agent instance to add
        """
        self.agents.append(agent)
    
    def remove_agent(self, agent_name: str) -> bool:
        """
        Remove an agent from the team.
        
        Args:
            agent_name: Name of agent to remove
            
        Returns:
            True if agent was removed, False if not found
        """
        for i, agent in enumerate(self.agents):
            if agent.name == agent_name:
                self.agents.pop(i)
                return True
        return False
    
    def get_agent(self, agent_name: str) -> Optional[Agent]:
        """
        Get an agent by name.
        
        Args:
            agent_name: Name of agent to retrieve
            
        Returns:
            Agent instance or None if not found
        """
        for agent in self.agents:
            if agent.name == agent_name:
                return agent
        return None
    
    def execute(
        self,
        task: Dict[str, Any],
        blackboard: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the team based on its pattern.
        
        Args:
            task: Task specification
            blackboard: Shared state/memory
            
        Returns:
            Execution summary with results from all agents
        """
        if self.pattern == TeamPattern.SEQUENTIAL:
            return self._execute_sequential(task, blackboard)
        elif self.pattern == TeamPattern.PARALLEL:
            return self._execute_parallel(task, blackboard)
        elif self.pattern == TeamPattern.MANAGER_WORKER:
            return self._execute_manager_worker(task, blackboard)
        elif self.pattern == TeamPattern.PIPELINE:
            return self._execute_pipeline(task, blackboard)
        else:
            raise ValueError(f"Unknown team pattern: {self.pattern}")
    
    def _execute_sequential(
        self,
        task: Dict[str, Any],
        blackboard: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute agents one after another in order.
        
        Each agent can read the output of previous agents from the blackboard.
        """
        results = []
        
        for agent in self.agents:
            # Execute agent
            result = agent.execute(task, blackboard)
            results.append(result.dict())
            
            # Record in history
            self.execution_history.append({
                "agent": agent.name,
                "status": result.status.value,
                "output": result.output
            })
            
            # Stop if agent failed
            if result.status == AgentStatus.FAILED:
                break
        
        return {
            "team": self.name,
            "pattern": self.pattern.value,
            "results": results,
            "success": all(r["status"] == AgentStatus.SUCCESS.value for r in results)
        }
    
    def _execute_parallel(
        self,
        task: Dict[str, Any],
        blackboard: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute all agents simultaneously.
        
        TODO for students: Implement parallel execution using threading or asyncio
        For now, this is a placeholder that executes sequentially.
        """
        # TODO: Implement true parallel execution
        # Hint: Use ThreadPoolExecutor or asyncio.gather()
        return self._execute_sequential(task, blackboard)
    
    def _execute_manager_worker(
        self,
        task: Dict[str, Any],
        blackboard: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Manager-Worker pattern: First agent (manager) delegates to others (workers).
        
        TODO for students: Implement manager-worker coordination
        - Manager decomposes task into subtasks
        - Workers execute subtasks in parallel
        - Manager aggregates results
        """
        if not self.agents:
            return {"error": "No agents in team"}
        
        # First agent is the manager
        manager = self.agents[0]
        workers = self.agents[1:]
        
        # TODO: Implement manager-worker logic
        # For now, execute manager then workers sequentially
        results = []
        
        # Manager plans the work
        manager_result = manager.execute(task, blackboard)
        results.append(manager_result.dict())
        
        # Workers execute in parallel (TODO: make truly parallel)
        for worker in workers:
            worker_result = worker.execute(task, blackboard)
            results.append(worker_result.dict())
        
        return {
            "team": self.name,
            "pattern": self.pattern.value,
            "results": results,
            "success": all(r["status"] == AgentStatus.SUCCESS.value for r in results)
        }
    
    def _execute_pipeline(
        self,
        task: Dict[str, Any],
        blackboard: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Pipeline pattern: Output of each agent becomes input for next.
        
        Similar to sequential, but explicitly passes data between agents.
        """
        results = []
        current_input = task
        
        for agent in self.agents:
            # Execute agent with current input
            result = agent.execute(current_input, blackboard)
            results.append(result.dict())
            
            # Use agent output as input for next agent
            if result.output:
                current_input = {**current_input, **result.output}
            
            # Stop if agent failed
            if result.status == AgentStatus.FAILED:
                break
        
        return {
            "team": self.name,
            "pattern": self.pattern.value,
            "results": results,
            "success": all(r["status"] == AgentStatus.SUCCESS.value for r in results)
        }
    
    def get_capabilities(self) -> List[str]:
        """
        Get all capabilities available in this team.
        
        Returns:
            List of all unique capabilities across all agents
        """
        capabilities = set()
        for agent in self.agents:
            capabilities.update(agent.capabilities)
        return list(capabilities)
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get team information for debugging/monitoring.
        
        Returns:
            Dictionary with team metadata
        """
        return {
            "name": self.name,
            "pattern": self.pattern.value,
            "description": self.description,
            "agent_count": len(self.agents),
            "agents": [agent.get_info() for agent in self.agents],
            "capabilities": self.get_capabilities()
        }
