from django.db import models
from django.core.exceptions import ValidationError

# Note: https://docs.djangoproject.com/en/5.2/ref/models/fields/#:~:text=primary_key
# Django will automatically add primary key fields


class Palika(models.Model):
    """
    Utility model to track administrative divisions
    """

    name = models.CharField(max_length=100, unique=True, help_text="e.g., Latipur")
    abbreviated_name = models.CharField(
        max_length=6, unique=True, help_text="e.g., LTT"
    )

    class Meta:
        verbose_name = "Palika"
        verbose_name_plural = "Palikas"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.abbreviated_name})"

    def clean(self):
        """Custom validation to ensure abbr. names are at least two chars"""
        super().clean()
        if self.abbreviated_name and len(self.abbreviated_name.strip()) < 2:
            raise ValidationError(
                {"abbreviated_name": "Abbreviated_name must be at least 2 characters."}
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

    class Meta:
        verbose_name = "Organization Type"
        verbose_name_plural = "Organization Types"
        ordering = ["type"]

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

    class SchoolChoices(models.TextChoices):
        PRIVATE = "private", "Private"
        PUBLIC = "public", "Public"
        COMMUNITY = "community", "Community"

    type = models.CharField(
        choices=SchoolChoices.choices,
        unique=True,
        help_text="School type: Private, Public, Community",
    )

    class Meta:
        verbose_name = "School Type"
        verbose_name_plural = "School Types"
        ordering = ["type"]

    def __str__(self):
        return self.get_type_display()


class Class(models.Model):
    """
    Link table for class (i.e. grade) levels
    """

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

    class Meta:
        verbose_name_plural = "Classes"
        ordering = ["class_number"]

    def __str__(self):
        return f"Class {self.class_number}"


class Weekday(models.Model):
    """
    Days of the week link table
    """

    class DayChoices(models.TextChoices):
        MONDAY = "Monday", "Monday"
        TUESDAY = "Tuesday", "Tuesday"
        WEDNESDAY = "Wednesday", "Wednesday"
        THURSDAY = "Thursday", "Thursday"
        FRIDAY = "Friday", "Friday"
        SATURDAY = "Saturday", "Saturday"
        SUNDAY = "Sunday", "Sunday"

    name = models.CharField(max_length=10, choices=DayChoices.choices, unique=True)

    class Meta:
        verbose_name_plural = "Weekdays"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @classmethod
    def get_weekday_order(cls):
        """Return weekdays in Monday-Sunday order"""
        order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        return cls.objects.filter(name__in=order).order_by(
            models.Case(
                *[
                    models.When(name=day, then=models.Value(i))
                    for i, day in enumerate(order)
                ]
            )
        )
