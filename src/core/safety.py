import logging
import re
from typing import List, Tuple

logger = logging.getLogger(__name__)

class ContentSafety:
    """
    Ensures generated content (prompts, text) is safe for kids.
    """

    BANNED_KEYWORDS = [
        "nsfw", "horror", "gore", "blood", "violence", "nude", "naked",
        "scary", "death", "kill", "murder", "weapon", "gun", "knife",
        "demon", "satan", "evil", "monster", "terrifying", "creepy"
    ]

    @classmethod
    def check_prompt(cls, prompt: str) -> Tuple[bool, List[str]]:
        """
        Check if a prompt contains unsafe keywords.

        Args:
            prompt: The text to check.

        Returns:
            Tuple (is_safe, found_keywords)
        """
        prompt_lower = prompt.lower()
        found = []

        for keyword in cls.BANNED_KEYWORDS:
            # Simple keyword matching for now (word boundary aware)
            if re.search(r'\b' + re.escape(keyword) + r'\b', prompt_lower):
                found.append(keyword)

        if found:
            logger.warning(f"Safety Check FAILED for prompt: '{prompt[:50]}...'. Found: {found}")
            return False, found

        return True, []

    @classmethod
    def sanitize_prompt(cls, prompt: str) -> str:
        """
        Attempt to remove unsafe keywords from a prompt.
        """
        prompt_lower = prompt.lower()
        original_prompt = prompt

        for keyword in cls.BANNED_KEYWORDS:
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            prompt = pattern.sub("", prompt)

        # Clean up extra spaces
        prompt = re.sub(r'\s+', ' ', prompt).strip()

        if prompt != original_prompt:
            logger.info(f"Sanitized prompt. Original length: {len(original_prompt)}, New: {len(prompt)}")

        return prompt
