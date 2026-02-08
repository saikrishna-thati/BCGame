import asyncio
import logging
import os
import shutil
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class RenderBackend(ABC):
    """
    Abstract Base Class for Rendering Backends.
    Now supports job tracing.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_concurrency = config.get("max_concurrent_renders", 1)
        self._semaphore = asyncio.Semaphore(self.max_concurrency)

    async def render_scene(self, scene_data: Dict[str, Any], engine_name: str, job_id: Optional[str] = None) -> str:
        """
        Execute the scene rendering job with job tracing.
        """
        async with self._semaphore:
            logger.info(f"[Job {job_id}] Dispatching render for scene {scene_data.get('id')} to {self.__class__.__name__} (Concurrency: {self.max_concurrency})")
            return await self._execute_render(scene_data, engine_name, job_id)

    @abstractmethod
    async def _execute_render(self, scene_data: Dict[str, Any], engine_name: str, job_id: Optional[str] = None) -> str:
        """Implement the actual execution logic."""
        pass

class LocalBackend(RenderBackend):
    """
    Executes rendering locally on the host machine.
    """

    async def _execute_render(self, scene_data: Dict[str, Any], engine_name: str, job_id: Optional[str] = None) -> str:
        """
        Simulate local process execution.
        """
        scene_id = scene_data.get("id")
        duration = scene_data.get("duration", 5)

        # Simulate processing time based on duration (scaled down for demo)
        delay = min(duration * 0.1, 2.0)
        await asyncio.sleep(delay)

        output_path = f"assets/output/{job_id}_scene_{scene_id}.mp4"
        # Mock file creation
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(f"Simulated video content for Job {job_id} scene {scene_id} using {engine_name}")

        logger.info(f"[Job {job_id}] [LocalBackend] Finished rendering scene {scene_id} ({duration}s)")
        return output_path

class ModalBackend(RenderBackend):
    """
    Executes rendering remotely on Modal.com.
    References 'src/animation/modal_stub_example.py' for implementation details.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Mock Modal client initialization
        self.modal_stub = None

    async def _execute_render(self, scene_data: Dict[str, Any], engine_name: str, job_id: Optional[str] = None) -> str:
        """
        Simulate remote dispatch to Modal.
        """
        scene_id = scene_data.get("id")
        logger.info(f"[Job {job_id}] [ModalBackend] Dispatching scene {scene_id} to cloud GPU...")

        # Simulate network latency + render time
        await asyncio.sleep(0.5)

        # In reality, we'd call the Modal function here
        # output_path = modal_stub.render_scene.remote(scene_data, engine_name)

        output_path = f"assets/output/{job_id}_scene_{scene_id}_modal.mp4"
        with open(output_path, 'w') as f:
            f.write(f"Simulated Modal video content for Job {job_id} scene {scene_id}")

        return output_path
