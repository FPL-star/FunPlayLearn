from django.db import models
from django.core.validators import URLValidator


class Game(models.Model):
    """
    Model to define and track games.
    """

    class Meta:
        verbose_name = "Game"
        verbose_name_plural = "Games"
        ordering = ["name"]

    name = models.CharField("Game Name", max_length=100, unique=True)
    description = models.TextField("Game Description", blank=True)
    how_to = models.TextField("How to Play", blank=True)
    team_prep = models.TextField("Team Preparation", blank=True)
    challenges = models.TextField("Challenges", blank=True)  # CSV
    questions = models.TextField("Questions", blank=True)  # Expect "?" separate values
    quality_checklist = models.TextField(
        "Quality Checklist", blank=True
    )  # Expect "?" separate values
    materials = models.TextField("Materials Required", blank=True)  # CSV
    video_url = models.URLField(
        "Video URL", blank=True, unique=True, validators=[URLValidator()]
    )
    image = models.ImageField(
        upload_to="games/",
        blank=True,
        null=True,
        help_text="Upload an image of the game",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
