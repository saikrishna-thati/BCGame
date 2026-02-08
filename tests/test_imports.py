import sys
import os
import unittest

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestImports(unittest.TestCase):
    def test_core_imports(self):
        try:
            from src.core.skill_interface import OpenClawSkill
            from src.skills.animation_skill import AnimationSkill
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Core imports failed: {e}")

    def test_character_imports(self):
        try:
            from src.characters.models import CharacterProfile
            from src.characters.manager import CharacterManager
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Character imports failed: {e}")

    def test_animation_imports(self):
        try:
            from src.animation.orchestrator import AnimationOrchestrator
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Animation imports failed: {e}")

if __name__ == '__main__':
    unittest.main()
