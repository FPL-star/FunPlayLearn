from django.test import TestCase
from django.core.exceptions import ValidationError
from games.models import Game
import unittest

class GameModelTest(TestCase):

    def setUp(self):
        """Create a sample game for testing"""
        self.game = Game.objects.create(
            game="Chess",
            description="A strategic board game",
            how_to="Move pieces according to rules",
            team_prep="No team prep needed",
            video_url="https://example.com/video",
            image_url="https://example.com/image",
            challenges={"time_limit": "60 mins"},
            questions={"q1": "How many pieces?"},
            quality_checklist={"rule_book": True},
            materials_required={"board": 1, "pieces": 32},
        )

    def test_game_creation(self):
        self.assertEqual(self.game.game, "Chess")
        self.assertEqual(self.game.description, "A strategic board game")
        self.assertTrue(self.game.is_active)

    def test_json_fields(self):
        self.assertEqual(self.game.challenges["time_limit"], "60 mins")
        self.assertEqual(self.game.questions["q1"], "How many pieces?")
        self.assertTrue(self.game.quality_checklist["rule_book"])
        self.assertEqual(self.game.materials_required["pieces"], 32)

    def test_str_method(self):
        self.assertEqual(str(self.game), "Chess")

    def test_validation_video_url(self):
        self.game.video_url = "invalid-url"
        with self.assertRaises(ValidationError):
            self.game.clean()

    def test_ordering(self):
        Game.objects.create(game="Checkers")
        games = Game.objects.all()
        self.assertEqual(list(games.values_list('game', flat=True)), ["Checkers", "Chess"])

    def test_blank_fields(self):
        g = Game.objects.create(game="Solitaire")
        self.assertEqual(g.description, "")
        self.assertEqual(g.how_to, "")
        self.assertEqual(g.team_prep, "")
        self.assertEqual(g.video_url, "")
        self.assertEqual(g.image_url, "")
        self.assertEqual(g.challenges, {})
        self.assertEqual(g.questions, {})

# Custom runner to print a success message
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(GameModelTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("\n🎉 All Game model tests passed successfully!")

