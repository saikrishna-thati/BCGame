from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class StyleGuide(BaseModel):
    """
    Global style settings for the video.
    """
    name: str = "Cinematic Kids Animation"
    base_prompt: str = "3d render, pixar style, bright colors, friendly, cinematic lighting, 8k, unreal engine 5, octane render"
    negative_prompt: str = "low quality, blurry, distorted, dark, horror, text, watermark, bad anatomy, deformed"
    lora_weights: Optional[Dict[str, float]] = None
    seed: int = 42

class CharacterProfile(BaseModel):
    """
    Profile for a specific character.
    """
    name: str
    description: str
    base_image_path: Optional[str] = None
    fixed_prompt_tags: List[str] = Field(default_factory=list)
    negative_prompt_tags: List[str] = Field(default_factory=list)
    seed: int
    voice_id: Optional[str] = None # For TTS
    clothing_variants: Dict[str, List[str]] = Field(default_factory=dict) # e.g. {"winter": ["scarf", "coat"]}

class SceneCharacterState(BaseModel):
    """
    State of a character in a specific scene.
    """
    character_name: str
    outfit: str = "default"
    emotion: str = "neutral"
    action: str = "standing"
