from django.db import models
from django.core.exceptions import ValidationError
from core.models import Palika, OrganizationType, Contact


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

        if self.contact and not self.contact.is_organization:
            raise ValidationError(
                {
                    "contact": "Contact must be marked as organization contact (is_organization=True)"
                }
            )


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
        if self.organization.name == "FunPlayLearn":
            return self.name
        return f"{self.organization.name} - {self.name}"
