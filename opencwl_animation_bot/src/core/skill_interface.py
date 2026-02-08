from abc import ABC, abstractmethod
from typing import Dict, Any, List

class OpenClawSkill(ABC):
    """
    Abstract Base Class for OpenClaw Skills.
    All skills must inherit from this and implement the execute method.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.config: Dict[str, Any] = {}

    def configure(self, config: Dict[str, Any]):
        """Configure the skill with necessary parameters."""
        self.config = config

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the skill logic.

        Args:
            context: A dictionary containing input parameters and context from the agent.

        Returns:
            A dictionary containing the results of the execution.
        """
        pass

    @abstractmethod
    def get_manifest(self) -> Dict[str, Any]:
        """Return the skill's manifest data."""
        pass
