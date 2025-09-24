from django.test import TestCase
from django.core.exceptions import ValidationError
from games.models import Game


class GameModelTest(TestCase):

    def setUp(self):
        """Create a sample game for testing"""
        self.game = Game.objects.create(
            name="Chess",
            description="A strategic board game",
            how_to="Move pieces according to rules",
            team_prep="No team prep needed",
            video_url="https://example.com/video",
            challenges="time_limit,60 mins",
            questions="How many pieces?",
            quality_checklist="rule_book",
            materials="board,32;pieces,32",  # simple CSV representation
        )

    def test_game_creation(self):
        self.assertEqual(self.game.name, "Chess")
        self.assertEqual(self.game.description, "A strategic board game")
        self.assertTrue(self.game.is_active)

    def test_str_method(self):
        self.assertEqual(str(self.game), "Chess")

    def test_validation_video_url(self):
        self.game.video_url = "invalid-url"
        with self.assertRaises(ValidationError):
            self.game.full_clean()  # .clean() only validates field-level, full_clean is safer

    def test_ordering(self):
        Game.objects.create(name="Checkers")
        games = Game.objects.all()
        # should be alphabetically by name
        self.assertEqual(
            list(games.values_list("name", flat=True)), ["Checkers", "Chess"]
        )

    def test_blank_fields(self):
        g = Game.objects.create(name="Solitaire")
        self.assertEqual(g.description, "")
        self.assertEqual(g.how_to, "")
        self.assertEqual(g.team_prep, "")
        self.assertEqual(g.video_url, "")
        self.assertEqual(g.challenges, "")
        self.assertEqual(g.questions, "")
        self.assertEqual(g.quality_checklist, "")
        self.assertEqual(g.materials, "")

    # Optional: test that CSV-like fields can be parsed correctly
    def test_csv_fields(self):
        self.assertIn("time_limit", self.game.challenges)
        self.assertIn("How many pieces?", self.game.questions)
