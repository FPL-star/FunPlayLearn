from django.test import TestCase
from core.models import Palika, OrganizationType
from organizations.models import Organization, OrganizationContact


class OrganizationModelTest(TestCase):
    """Simple test for Organization model."""

    def test_organization_creation(self):
        """Test creating an organization."""
        palika = Palika.objects.get(palika="Lalitpur")
        org_type = OrganizationType.objects.get(name="School")
        contact = OrganizationContact.objects.create(
            email="test@example.com",
            phone_number="9841234567",
            address="Test Address",
            is_organization=True,
        )

        org = Organization.objects.create(
            name="Test School", palika=palika, contact=contact, org_type=org_type
        )

        self.assertEqual(org.name, "Test School")
        self.assertTrue(org.active)
