import asyncio
import logging
import os
import uuid
from typing import Dict, Any, List, Optional

from src.animation.render_backend import RenderBackend, LocalBackend, ModalBackend
from src.characters.manager import CharacterManager

logger = logging.getLogger(__name__)

class AnimationOrchestrator:
    """
    Manages the end-to-end animation pipeline.
    Includes retry logic, fallback mechanisms, and job tracing.
    """

    def __init__(self, config: Dict[str, Any], character_manager: CharacterManager):
        self.config = config
        self.character_manager = character_manager
        self.max_retries = config.get("max_retries", 3)

        # Initialize the render backend based on config
        backend_type = config.get("render_backend", "local").lower()
        backend_config = config.get("backend_config", {})

        if backend_type == "modal":
            self.backend = ModalBackend(backend_config)
            logger.info("Initialized ModalBackend for cloud rendering.")
        else:
            self.backend = LocalBackend(backend_config)
            logger.info("Initialized LocalBackend for local rendering.")

    async def generate_video(self, script: str, output_path: str, job_id: Optional[str] = None) -> str:
        """
        Orchestrate the video generation process with error handling and job tracing.
        """
        job_id = job_id or str(uuid.uuid4())[:8]
        logger.info(f"[Job {job_id}] Starting video generation pipeline with {self.backend.__class__.__name__}")

        # Step 1: Segmentation
        scenes = self._segment_script(script)
        logger.info(f"[Job {job_id}] Generated {len(scenes)} scenes.")

        # Step 2: Render Scenes in Parallel with Retry
        tasks = []
        for i, scene in enumerate(scenes):
            tasks.append(self._render_scene_safely(scene, job_id))

        # Execute all tasks
        scene_paths_or_errors = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter successful paths and handle critical failures
        valid_scene_paths = []
        for i, result in enumerate(scene_paths_or_errors):
            if isinstance(result, Exception):
                logger.error(f"[Job {job_id}] Scene {i} failed after retries: {result}")
                fallback_path = self._create_fallback_scene(i, job_id)
                valid_scene_paths.append(fallback_path)
            else:
                valid_scene_paths.append(result)

        # Step 3: Assembly
        final_video = self._assemble_video(valid_scene_paths, output_path, job_id)
        logger.info(f"[Job {job_id}] Video generation complete: {final_video}")
        return final_video

    async def _render_scene_safely(self, scene: Dict[str, Any], job_id: str) -> str:
        """
        Attempt to render a scene with retries.
        """
        engine_name = scene.get("engine", "blender")
        scene_id = scene.get("id")

        for attempt in range(1, self.max_retries + 1):
            try:
                # Pass job_id to backend if supported (for now we assume backend logs it)
                # But wait, RenderBackend.render_scene signature needs update too?
                # For now, let's keep render_scene signature simpler or update it.
                # I'll update RenderBackend signature next.
                return await self.backend.render_scene(scene, engine_name, job_id)
            except Exception as e:
                logger.warning(f"[Job {job_id}] Render attempt {attempt}/{self.max_retries} failed for scene {scene_id}: {e}")
                if attempt == self.max_retries:
                    raise
                await asyncio.sleep(1 * attempt)

    def _create_fallback_scene(self, scene_id: int, job_id: str) -> str:
        """Create a placeholder video file for failed scenes."""
        path = f"assets/output/{job_id}_scene_{scene_id}_fallback.mp4"
        with open(path, 'w') as f:
            f.write(f"Fallback Content for Job {job_id} due to render failure")
        logger.info(f"[Job {job_id}] Created fallback content for scene {scene_id}")
        return path

    def _segment_script(self, script: str) -> List[Dict[str, Any]]:
        """Mock implementation."""
        return [
            {"id": i, "duration": 10, "engine": "blender", "characters": ["Boy", "Robot"]}
            for i in range(5)
        ]

    def _assemble_video(self, scene_paths: List[str], output_path: str, job_id: str) -> str:
        """Combine scene videos."""
        logger.info(f"[Job {job_id}] Assembling {len(scene_paths)} scenes into {output_path}")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(f"Final assembled video for Job {job_id} from {len(scene_paths)} scenes.")
        return output_path
