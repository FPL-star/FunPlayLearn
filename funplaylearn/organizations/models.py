from django.db import models
from django.core.exceptions import ValidationError

from core.models import Palika, OrganizationType, SchoolType, Class, Contact


class OrganizationContact(Contact):
    """Proxy model to assign org contacts to organization app"""

    class Meta:
        proxy = True
        verbose_name = "Organization Contact"
        verbose_name_plural = "Organization Contacts"


class Organization(models.Model):
    """
    Model representing an organization with geographic location data.
    """

    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"
        ordering = ["name"]

    palika = models.ForeignKey(
        Palika,
        on_delete=models.PROTECT,
        help_text="Administrative division where organization is located",
        blank=True,
        null=True,
    )

    contact = models.OneToOneField(
        OrganizationContact,
        on_delete=models.CASCADE,
        help_text="Contact information for this organization",
    )

    org_type = models.ForeignKey(
        OrganizationType,
        on_delete=models.PROTECT,
        help_text="Type of organization (School, College, NGO, FPL)",
    )

    name = models.CharField(max_length=255, help_text="Full name of the organization")

    latitude = models.FloatField(null=True, blank=True, help_text="Latitude coordinate")

    longitude = models.FloatField(
        null=True, blank=True, help_text="Longitude coordinate"
    )

    general_location = models.CharField(
        max_length=255,
        blank=True,
        null=False,
        help_text="Landmark or general location description",
    )

    active = models.BooleanField(
        default=True, help_text="Whether this organization is currently active"
    )

    def __str__(self):
        if self.palika:
            return f"{self.name} ({self.palika.short_name.upper()})"
        return self.name

    def clean(self):
        """Custom validation to prevent creation of person contact as organization contact"""
        super().clean()
        if self.contact_id and not self.contact.is_organization:
            self.contact.is_organization = True


class Role(models.Model):
    """
    Model representing a role within an organization.
    """

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "organization"], name="unique_role_per_organization"
            )
        ]

    name = models.CharField(
        max_length=100, help_text="Name of the role (e.g., Teacher, Student, Staff)"
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        help_text="Organization this role is associated with",
    )

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class School(models.Model):
    """
    Model for organizations that are schools.
    """

    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name="org_school",
    )
    school_type = models.ForeignKey(
        SchoolType,
        on_delete=models.PROTECT,
        help_text="Type of school (e.g., Private, Government, Community)",
    )
    class_1_fee = models.IntegerField(
        null=True, blank=True, help_text="Fee for class 1"
    )
    provides_food = models.BooleanField(help_text="Whether the school provides food")
    first_session_date = models.DateField(
        null=False, blank=False, help_text="Date of the first session"
    )
    start_time_firsthalf = models.TimeField(
        null=False, blank=False, help_text="Start time for the first half of the day"
    )
    start_time_secondhalf = models.TimeField(
        null=False, blank=False, help_text="Start time for the second half of the day"
    )
    session_duration = models.IntegerField(
        null=False, blank=False, help_text="Duration of each session in minutes"
    )

    class Meta:
        verbose_name = "School"
        verbose_name_plural = "Schools"
        ordering = ["organization"]

    def __str__(self):
        return f"{self.organization.name}"


class Schoolclass(models.Model):
    """
    Model representing a class (grade level) within a school.
    """

    school = models.ForeignKey(
        School,
        on_delete=models.PROTECT,
        help_text="School this class is associated with",
    )
    Class = models.ForeignKey(
        Class, on_delete=models.PROTECT, help_text="Class/Grade level"
    )
    max_students = models.IntegerField(
        null=False, blank=False, help_text="Maximum number of students in the class"
    )

    class Meta:
        verbose_name = "School Class"
        verbose_name_plural = "School Classes"
        ordering = ["school"]
        constraints = [
            models.UniqueConstraint(
                fields=["Class", "school"], name="unique_class_per_school"
            )
        ]

    def __str__(self):
        return f"{self.school.organization.name} "
