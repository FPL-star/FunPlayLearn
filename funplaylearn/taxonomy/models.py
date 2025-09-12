from django.db import models
from django.core.exceptions import ValidationError

# Note: https://docs.djangoproject.com/en/5.2/ref/models/fields/#:~:text=primary_key
# Django will automatically add primary key fields


class Palika(models.Model):
    """
    Utility model to track administrative divisions
    """

    class Meta:
        verbose_name = "Palika"
        verbose_name_plural = "Palikas"
        ordering = ["palika"]

    palika = models.CharField(
        "Palika", max_length=100, unique=True, help_text="e.g., Latipur"
    )
    short_name = models.CharField(
        "Abbreviation", max_length=6, unique=True, help_text="e.g., LTT"
    )

    def __str__(self):
        return f"{self.palika.title()} ({self.short_name.upper()})"

    def clean(self):
        """Custom validation to ensure abbr. names are at least two chars"""
        super().clean()
        if self.short_name and len(self.short_name.strip()) < 2:
            raise ValidationError(
                {"short_name": "Short name must be at least 2 characters."}
            )


class OrganizationType(models.Model):
    """
    Utility model to track organization type.
    Options are:
        School
        College
        NGO
        FPL
    """

    class Meta:
        verbose_name = "Organization Type"
        verbose_name_plural = "Organization Types"
        ordering = ["type"]

    class OrganizationChoices(models.TextChoices):
        SCHOOL = "school", "School"
        COLLEGE = "college", "College"
        NGO = "ngo", "NGO"
        FPL = "fpl", "FPL"

    type = models.CharField(
        choices=OrganizationChoices.choices,
        unique=True,
        help_text="Organization Type: School, College, NGO, FPL",
    )

    def __str__(self):
        return self.get_type_display()


class SchoolType(models.Model):
    """
    Utility model to track school type.
    Options are:
        Private
        Public
        Community
    """

    class Meta:
        verbose_name = "School Type"
        verbose_name_plural = "School Types"
        ordering = ["type"]

    class SchoolChoices(models.TextChoices):
        PRIVATE = "private", "Private"
        PUBLIC = "public", "Public"
        COMMUNITY = "community", "Community"

    type = models.CharField(
        choices=SchoolChoices.choices,
        unique=True,
        help_text="School type: Private, Public, Community",
    )

    def __str__(self):
        return self.get_type_display()


class Class(models.Model):
    """
    Link table for class (i.e. grade) levels
    """

    class Meta:
        verbose_name_plural = "Classes"
        ordering = ["class_number"]

    class ClassChoices(models.IntegerChoices):
        CLASS_1 = 1, "Class 1"
        CLASS_2 = 2, "Class 2"
        CLASS_3 = 3, "Class 3"
        CLASS_4 = 4, "Class 4"
        CLASS_5 = 5, "Class 5"
        CLASS_6 = 6, "Class 6"
        CLASS_7 = 7, "Class 7"
        CLASS_8 = 8, "Class 8"
        CLASS_9 = 9, "Class 9"
        CLASS_10 = 10, "Class 10"

    class_number = models.PositiveIntegerField(
        choices=ClassChoices.choices, unique=True, help_text="Class/Grade level (1-10)"
    )

    def __str__(self):
        return f"Class {self.class_number}"


class Weekday(models.Model):
    """
    Days of the week link table
    """

    class Meta:
        verbose_name_plural = "Weekdays"
        ordering = ["pk"]

    class DayChoices(models.TextChoices):
        MONDAY = "Monday", "Monday"
        TUESDAY = "Tuesday", "Tuesday"
        WEDNESDAY = "Wednesday", "Wednesday"
        THURSDAY = "Thursday", "Thursday"
        FRIDAY = "Friday", "Friday"
        SATURDAY = "Saturday", "Saturday"
        SUNDAY = "Sunday", "Sunday"

    name = models.CharField(max_length=10, choices=DayChoices.choices, unique=True)

    def __str__(self):
        return self.name
