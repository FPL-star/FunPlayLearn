
from django.db import models
from django.core.exceptions import ValidationError

class Game(models.Model):
    """
    Model to define and track games.
    """

    class Meta:
        verbose_name = "Game"
        verbose_name_plural = "Games"
        ordering = ["game"]

    game = models.CharField("Game Name", max_length=100, unique=True)
    description = models.TextField("Game Description", blank=True)
    how_to = models.TextField("How to Play", blank=True)
    team_prep = models.TextField("Team Preparation", blank=True)
    video_url = models.URLField("Video URL", blank=True)
    image_url = models.URLField("Image URL", blank=True)
    challenges = models.JSONField("Challenges", blank=True, default=dict)
    questions = models.JSONField("Questions", blank=True, default=dict)
    quality_checklist = models.JSONField("Quality Checklist", blank=True, default=dict)
    materials_required = models.JSONField("Materials Required", blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.game

    def clean(self):
        """
        Custom validation can go here.
        For example, ensure video_url is valid or challenges are not empty.
        """
        super().clean()
        if self.video_url and not self.video_url.startswith("http"):
            raise ValidationError({"video_url": "Video URL must be a valid URL."})

