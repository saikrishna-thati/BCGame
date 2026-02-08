from abc import ABC, abstractmethod
from typing import Dict, Any, List

class AnimationEngine(ABC):
    """
    Abstract Base Class for Animation Engines (Blender, Manim, etc.).
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    async def render_scene(self, scene_data: Dict[str, Any]) -> str:
        """
        Render a single scene.

        Args:
            scene_data: A dictionary containing scene details (script, characters, duration).

        Returns:
            The path to the rendered video file.
        """
        pass

    @abstractmethod
    def validate_scene(self, scene_data: Dict[str, Any]) -> bool:
        """Check if the scene can be rendered by this engine."""
        pass
