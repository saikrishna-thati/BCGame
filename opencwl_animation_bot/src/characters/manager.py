import logging
import json
import random
from typing import Dict, List, Optional
from src.characters.models import CharacterProfile, StyleGuide, SceneCharacterState
from src.core.safety import ContentSafety

logger = logging.getLogger(__name__)

class CharacterManager:
    """
    Manages character profiles and ensures consistency across video generation.
    Incorporates safety checks for kid-friendly content.
    """

    def __init__(self, style_guide: Optional[StyleGuide] = None):
        self.style_guide = style_guide or StyleGuide()
        self.profiles: Dict[str, CharacterProfile] = {}
        self.seed_registry: Dict[str, int] = {} # For tracking scene-specific seeds

    def register_character(self, profile: CharacterProfile):
        """Register a new character profile."""
        logger.info(f"Registering character: {profile.name}")
        self.profiles[profile.name] = profile

    def load_profiles_from_file(self, filepath: str):
        """Load character profiles from a JSON file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                for char_data in data:
                    self.register_character(CharacterProfile(**char_data))
        except Exception as e:
            logger.error(f"Failed to load profiles from {filepath}: {e}")

    def get_prompt_for_character(self, scene_state: SceneCharacterState) -> str:
        """
        Construct a Stable Diffusion prompt for a specific character in a scene.
        Combines global style, character fixed traits, and scene-specific actions.
        Applies safety filtering.
        """
        char = self.profiles.get(scene_state.character_name)
        if not char:
            raise ValueError(f"Character '{scene_state.character_name}' not found.")

        # Construct Prompt
        # 1. Base style
        prompt_parts = [self.style_guide.base_prompt]

        # 2. Character Description
        prompt_parts.append(f"character {char.name}, {char.description}")
        prompt_parts.extend(char.fixed_prompt_tags)

        # 3. Outfit handling
        outfit_tags = char.clothing_variants.get(scene_state.outfit, [])
        prompt_parts.extend(outfit_tags)

        # 4. Action & Emotion
        prompt_parts.append(f"{scene_state.emotion} expression, {scene_state.action}")

        # Final Prompt Assembly
        full_prompt = ", ".join(prompt_parts)

        # Safety Check
        is_safe, found = ContentSafety.check_prompt(full_prompt)
        if not is_safe:
            full_prompt = ContentSafety.sanitize_prompt(full_prompt)
            logger.warning(f"Sanitized unsafe prompt for {char.name}: {found}")

        return full_prompt

    def get_negative_prompt(self, character_name: str) -> str:
        """Get the negative prompt for a character generation."""
        char = self.profiles.get(character_name)
        neg_parts = [self.style_guide.negative_prompt]
        if char:
            neg_parts.extend(char.negative_prompt_tags)
        return ", ".join(neg_parts)

    def get_reference_image(self, character_name: str) -> Optional[str]:
        """Get the path to the reference image for consistency checks."""
        char = self.profiles.get(character_name)
        if char:
            return char.reference_image_path
        return None

    def get_seed(self, character_name: str, scene_id: str) -> int:
        """
        Get a consistent seed for a character in a scene.
        Currently returns the character's base seed, but could be modified to vary per scene if needed while maintaining identity.
        """
        # For strict consistency, we often reuse the base seed or a small set of seeds
        # Here we just use the character's primary seed
        char = self.profiles.get(character_name)
        if char:
            return char.seed
        return self.style_guide.seed

    def validate_consistency(self, image_path: str, character_name: str) -> float:
        """
        Check if the generated image matches the character's reference.
        Returns a similarity score (0.0 to 1.0).
        """
        # This would use CLIP or a similar model to compare embeddings.
        # For now, we simulate a successful check.
        logger.info(f"Validating consistency for {character_name} in {image_path}")

        # Mock logic: return a high score
        return 0.95
