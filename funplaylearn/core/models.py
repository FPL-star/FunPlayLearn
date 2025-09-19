from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

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
        "Palika", max_length=100, unique=True, help_text="e.g., Lalitpur"
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
        ordering = ["name"]

    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Organization Type: School, College, NGO, FPL",
    )

    def __str__(self):
        return self.name


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
        ordering = ["name"]

    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="School type: Private, Public, Community",
    )

    def __str__(self):
        return self.name


class Class(models.Model):
    """
    Link table for class (i.e. grade) levels
    """

    class Meta:
        verbose_name_plural = "Classes"
        ordering = ["class_number"]

    class_number = models.PositiveIntegerField(
        unique=True, help_text="Class/Grade level (1-10)"
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

    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class Contact(models.Model):
    """
    Contact information for People and Organizations
    """

    PHONE_REGEX_VALIDATOR = RegexValidator(
        r"^\d{3,15}$", "Enter a valid phone number (3-15 digits)"
    )

    class Meta:
        verbose_name_plural = "Contacts"

    is_organization = models.BooleanField(
        default=False,
        help_text="Set to True if contact is an organization, False if it is a person",
    )
    email = models.EmailField(
        max_length=254,  # RFC email max length
        blank=True,
        null=False,
        help_text="Email address (RFC 5321 max length 254 characters",
    )
    phone_country_code = models.CharField(
        max_length=4,
        default="977",  # Nepal country code
        help_text="Country calling code digits (i.e. 977 for Nepal)",
        validators=[RegexValidator(r"^\d{1,4}$", "Enter 1-4 digits for country code")],
    )
    phone_number = models.CharField(
        max_length=15,
        help_text="Local phone number without country code",
        validators=[PHONE_REGEX_VALIDATOR],
    )
    address = models.TextField(help_text="Postal address")
    emergency_contact_name = models.CharField(
        max_length=255,
        blank=True,
        null=False,
        help_text="Name of emergency contact person",
    )
    emergency_contact_phone = models.CharField(
        max_length=15,
        blank=True,
        null=False,
        help_text="Emergency contact phone number without country code",
        validators=[PHONE_REGEX_VALIDATOR],
    )
    emergency_contact_relationship = models.CharField(
        max_length=100,
        blank=True,
        null=False,
        help_text="Relationship of the emergency contact",
    )

    def __str__(self):
        label = "Organization" if self.is_organization else "Person"
        return f"{label}: [email]: {self.email} [phone number]: {self.full_phone}"

    @property
    def full_phone(self):
        """
        Return full phone number (with country code) if possible
        """
        if self.phone_number:
            return f"+{self.phone_country_code} {self.phone_number}"
        return None


class OrganizationContact(Contact):
    """Proxy model to assign org contacts to organization app"""

    class Meta:
        proxy = True
        verbose_name = "Organization Contact"
        verbose_name_plural = "Organization Contacts"


class PersonContact(Contact):
    """Proxy model to assign person contacts to people app"""

    class Meta:
        proxy = True
        verbose_name = "Person Contact"
        verbose_name_plural = "Person Contacts"
