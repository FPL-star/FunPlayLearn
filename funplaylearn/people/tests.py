# people/tests.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date
from unittest.mock import patch
from cryptography.fernet import Fernet

from people.models import Person, FPLMember, PersonSensitiveData, PersonEducation
from core.models import Palika, Contact, OrganizationContact, OrganizationType
from organizations.models import Role, Organization


class BaseModelTest(TestCase):
    """Helper base class for common setup"""

    def setUp(self):
        # Use seeded data
        self.palika = Palika.objects.first()
        self.org_type = OrganizationType.objects.get(name="FPL")

        # Create org contact marked as organization
        self.org_contact = OrganizationContact.objects.create(
            phone_number="1111111111", email="org@test.com", is_organization=True
        )

        # Create organization
        self.organization = Organization.objects.create(
            name="Test Org",
            palika=self.palika,
            contact=self.org_contact,
            org_type=self.org_type,
        )

        # Create a role inside organization
        self.role = Role.objects.create(
            name="Test Role", organization=self.organization
        )


class PersonModelTest(BaseModelTest):
    def test_person_creation(self):
        """Test basic person creation"""
        person = Person.objects.create(
            first_name="John", last_name="Doe", role=self.role, gender="M"
        )
        self.assertEqual(person.full_name, "John Doe")
        self.assertEqual(str(person), f"John Doe [{self.role.name}]")

    def test_person_with_contact(self):
        """Test person creation with personal contact"""
        contact = Contact.objects.create(
            phone_number="9841234567", email="test@example.com"
        )
        person = Person.objects.create(
            first_name="Jane", last_name="Smith", role=self.role, contact=contact
        )
        self.assertEqual(person.contact, contact)

    def test_person_default_values(self):
        """Test person default values"""
        person = Person.objects.create(first_name="Test", last_name="User")
        self.assertEqual(person.gender, "N")
        self.assertEqual(person.bio, "")
        # default role assignment
        self.assertEqual(str(person.role), "Temporary Role")

    def test_person_required_fields(self):
        """Test required fields enforced"""
        person = Person(first_name="John")
        with self.assertRaises(ValidationError):
            person.full_clean()


class FPLMemberModelTest(BaseModelTest):
    def setUp(self):
        super().setUp()
        self.person = Person.objects.create(
            first_name="John", last_name="Doe", role=self.role
        )

    def test_fpl_member_creation(self):
        member = FPLMember.objects.create(
            person=self.person, palika=self.palika, start_date=date(2023, 1, 1)
        )
        self.assertTrue(member.active)
        self.assertFalse(member.sim_returned)

    def test_fpl_member_str(self):
        member = FPLMember.objects.create(
            person=self.person, palika=self.palika, start_date=date(2023, 1, 1)
        )
        self.assertEqual(str(member), f"{self.person.full_name} [Active: True]")

    def test_one_to_one_relationship(self):
        FPLMember.objects.create(
            person=self.person, palika=self.palika, start_date=date(2023, 1, 1)
        )
        with self.assertRaises(IntegrityError):
            FPLMember.objects.create(
                person=self.person, palika=self.palika, start_date=date(2023, 2, 1)
            )


class PersonSensitiveDataModelTest(BaseModelTest):
    def setUp(self):
        super().setUp()
        self.person = Person.objects.create(
            first_name="John", last_name="Doe", role=self.role
        )
        self.fpl_member = FPLMember.objects.create(
            person=self.person, palika=self.palika, start_date=date(2023, 1, 1)
        )

    def test_sensitive_data_creation(self):
        data = PersonSensitiveData.objects.create(
            fpl_member=self.fpl_member, date_of_birth=date(1990, 5, 15), blood_type="O+"
        )
        self.assertEqual(data.blood_type, "O+")

    def test_encrypted_fields(self):
        key = Fernet.generate_key()
        fernet = Fernet(key)
        with patch("core.utils.encryption._get_fernet", return_value=fernet):
            data = PersonSensitiveData.objects.create(
                fpl_member=self.fpl_member,
                date_of_birth=date(1990, 5, 15),
                blood_type="A+",
            )
            # assign encrypted fields
            data.bank_account = "1234567890"
            data.pan_number = "ABCDE1234F"
            data.save()
            data.refresh_from_db()
            self.assertEqual(data.bank_account, "1234567890")
            self.assertEqual(data.pan_number, "ABCDE1234F")
            self.assertIsInstance(data._bank_account, bytes)
            self.assertIsInstance(data._pan_number, bytes)

    def test_blood_compatibility(self):
        data = PersonSensitiveData.objects.create(
            fpl_member=self.fpl_member,
            date_of_birth=date(1990, 5, 15),
            blood_type="O-",
        )
        self.assertIn("AB+", data.can_donate_to)
        self.assertEqual(data.can_receive_from, ["O-"])

    def test_ab_positive_compatibility(self):
        data = PersonSensitiveData.objects.create(
            fpl_member=self.fpl_member,
            date_of_birth=date(1990, 5, 15),
            blood_type="AB+",
        )
        self.assertEqual(data.can_donate_to, ["AB+"])
        self.assertIn("O-", data.can_receive_from)

    def test_sensitive_data_str(self):
        data = PersonSensitiveData.objects.create(
            fpl_member=self.fpl_member, date_of_birth=date(1990, 5, 15), blood_type="A+"
        )
        self.assertIn("John Doe", str(data))

    def test_encrypted_fields_with_none(self):
        data = PersonSensitiveData.objects.create(
            fpl_member=self.fpl_member, date_of_birth=date(1990, 5, 15), blood_type="B+"
        )
        data.bank_account = None
        data.pan_number = None
        data.save()
        data.refresh_from_db()
        self.assertIsNone(data.bank_account)
        self.assertIsNone(data.pan_number)


class PersonEducationModelTest(BaseModelTest):
    def setUp(self):
        super().setUp()
        self.person = Person.objects.create(
            first_name="Alice", last_name="Johnson", role=self.role
        )
        self.fpl_member = FPLMember.objects.create(
            person=self.person, palika=self.palika, start_date=date(2023, 1, 1)
        )

    def test_education_creation(self):
        edu = PersonEducation.objects.create(
            fpl_member=self.fpl_member,
            level="BA",
            institution="Test University",
            field_of_study="Computer Science",
        )
        self.assertEqual(edu.level, "BA")

    def test_education_str(self):
        edu = PersonEducation.objects.create(
            fpl_member=self.fpl_member,
            level="MA",
            institution="Grad School",
            is_current=True,
        )
        self.assertIn("Grad School", str(edu))

    def test_education_default_values(self):
        edu = PersonEducation.objects.create(fpl_member=self.fpl_member, level="PHD")
        self.assertEqual(edu.institution, "")
        self.assertFalse(edu.is_current)

    def test_education_choices(self):
        valid_levels = ["SCHOOL", "PLUS_TWO", "BA", "MA", "PHD", "OTHER"]
        for lvl in valid_levels:
            edu = PersonEducation.objects.create(fpl_member=self.fpl_member, level=lvl)
            self.assertEqual(edu.level, lvl)
            edu.delete()

    def test_one_to_one_education_relationship(self):
        PersonEducation.objects.create(fpl_member=self.fpl_member, level="BA")
        with self.assertRaises(IntegrityError):
            PersonEducation.objects.create(fpl_member=self.fpl_member, level="MA")


class ModelsIntegrationTest(BaseModelTest):
    def test_complete_person_workflow(self):
        key = Fernet.generate_key()
        with patch("core.utils.encryption._get_fernet", return_value=Fernet(key)):
            # create person + related
            contact = Contact.objects.create(
                phone_number="999888777", email="integration@test.com"
            )
            person = Person.objects.create(
                first_name="Complete", last_name="Test", role=self.role, contact=contact
            )
            member = FPLMember.objects.create(
                person=person, palika=self.palika, start_date=date(2023, 6, 1)
            )
            sensitive = PersonSensitiveData.objects.create(
                fpl_member=member, date_of_birth=date(1995, 8, 20), blood_type="AB-"
            )
            sensitive.bank_account = "9876543210123456"
            sensitive.pan_number = "ZYXWV9876E"
            sensitive.save()
            edu = PersonEducation.objects.create(
                fpl_member=member,
                level="MA",
                institution="Integration University",
                field_of_study="Development Studies",
            )

            # assertions
            self.assertEqual(person.fpl_member, member)
            self.assertEqual(member.personsensitivedata, sensitive)
            self.assertEqual(member.education, edu)
            self.assertEqual(sensitive.bank_account, "9876543210123456")
            self.assertIn("AB+", sensitive.can_donate_to)
