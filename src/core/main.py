import sys
import os
import asyncio
import logging
from typing import Dict, Any

# Ensure the project root is in the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.core.skill_interface import OpenClawSkill
from src.skills.animation_skill import AnimationSkill

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SkillRegistry:
    """Mock registry to manage OpenClaw skills."""
    def __init__(self):
        self._skills: Dict[str, OpenClawSkill] = {}

    def register(self, skill: OpenClawSkill):
        logger.info(f"Registering skill: {skill.name}")
        self._skills[skill.name] = skill

    def get_skill(self, name: str) -> OpenClawSkill:
        return self._skills.get(name)

async def main():
    logger.info("Initializing OpenClaw Animation Bot...")

    # Initialize Registry
    registry = SkillRegistry()

    # Initialize and Register Animation Skill
    anim_skill = AnimationSkill()
    registry.register(anim_skill)

    # Configure Skill (mock config matching settings.yaml structure)
    config = {
        "output_dir": "assets/output",
        "character_profiles_path": "assets/characters/profiles.json",
        "animation": {
            "resolution": "2560x810",
            "fps": 24,
            "render_backend": "local",
            "backend_config": {
                "max_concurrent_renders": 2
            }
        }
    }
    anim_skill.configure(config)

    logger.info("Bot is ready. Waiting for commands (simulated).")

    # Simulate a command execution (e.g., from Telegram)
    # In a real scenario, this would loop and listen for events
    test_context = {
        "topic": "The Solar System for Kids",
        "duration": 60 # shortened for test
    }

    result = await anim_skill.execute(test_context)
    logger.info(f"Execution Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
