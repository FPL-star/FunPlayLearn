from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date, datetime
from unittest.mock import patch
from cryptography.fernet import Fernet

from people.models import Person, FPLMember, PersonSensitiveData, PersonEducation
from core.models import Palika, Contact

# from organization.models import Role  # TODO: Uncomment when Role model is ready


class PersonModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        # TODO: When Role model is ready, replace with:
        # self.role = Role.objects.create(name="Test Role", description="Test role description")
        self.role = "Test Role"  # Temporary string for testing
        self.contact = Contact.objects.create(
            phone_number="9841234567", email="test@example.com"
        )

    def test_person_creation(self):
        """Test basic person creation"""
        person = Person.objects.create(
            first_name="John",
            last_name="Doe",
            role=self.role,
            gender="M",
        )
        self.assertEqual(person.first_name, "John")
        self.assertEqual(person.last_name, "Doe")
        self.assertEqual(person.full_name, "John Doe")
        self.assertEqual(str(person), "John Doe [Test Role]")

    def test_person_with_contact(self):
        """Test person creation with contact"""
        person = Person.objects.create(
            first_name="Jane",
            last_name="Smith",
            role=self.role,
            contact=self.contact,
            bio="Test bio",
        )
        self.assertEqual(person.contact, self.contact)
        self.assertEqual(person.bio, "Test bio")

    def test_person_default_values(self):
        """Test person default values"""
        person = Person.objects.create(
            first_name="Test",
            last_name="User",
        )
        self.assertEqual(person.gender, "N")
        self.assertEqual(person.bio, "")
        self.assertEqual(person.role, "Temporary Role")

    def test_person_required_fields(self):
        """Test that required fields are enforced"""
        person = Person(first_name="John")  # missing last_name
        with self.assertRaises(ValidationError):
            person.full_clean()


class FPLMemberModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        # TODO: When Role model is ready, replace with:
        # self.role = Role.objects.create(name="Member", description="Member role")
        self.role = "Member"  # Temporary string for testing
        self.person = Person.objects.create(
            first_name="John",
            last_name="Doe",
            role=self.role,
        )
        self.palika = Palika.objects.create(palika="Latipur", short_name="LTT")

    def test_fpl_member_creation(self):
        """Test FPL member creation"""
        member = FPLMember.objects.create(
            person=self.person,
            palika=self.palika,
            start_date=date(2023, 1, 1),
            agreement=True,
        )
        self.assertEqual(member.person, self.person)
        self.assertEqual(member.palika, self.palika)
        self.assertTrue(member.active)  # Default value
        self.assertTrue(member.agreement)
        self.assertFalse(member.sim_returned)  # Default value

    def test_fpl_member_str(self):
        """Test FPL member string representation"""
        member = FPLMember.objects.create(
            person=self.person, palika=self.palika, start_date=date(2023, 1, 1)
        )
        expected_str = f"{self.person.full_name} [Active: True]"
        self.assertEqual(str(member), expected_str)

    def test_one_to_one_relationship(self):
        """Test that person can only have one FPL member record"""
        FPLMember.objects.create(
            person=self.person, palika=self.palika, start_date=date(2023, 1, 1)
        )

        # Creating another FPL member with same person should fail
        with self.assertRaises(IntegrityError):
            FPLMember.objects.create(
                person=self.person, palika=self.palika, start_date=date(2023, 2, 1)
            )


class PersonSensitiveDataModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        # self.role = Role.objects.create(name="Member", description="Member role")  # TODO: Uncomment when Role model is ready
        self.person = Person.objects.create(
            first_name="John",
            last_name="Doe",
            role="Member",  # TODO: Change back to role=self.role when Role model is ready
        )
        self.palika = Palika.objects.create(palika="Latipur", short_name="LTT")
        self.fpl_member = FPLMember.objects.create(
            person=self.person, palika=self.palika, start_date=date(2023, 1, 1)
        )

    def test_sensitive_data_creation(self):
        """Test sensitive data creation"""
        sensitive_data = PersonSensitiveData.objects.create(
            fpl_member=self.fpl_member, date_of_birth=date(1990, 5, 15), blood_type="O+"
        )
        self.assertEqual(sensitive_data.fpl_member, self.fpl_member)
        self.assertEqual(sensitive_data.blood_type, "O+")
        self.assertEqual(sensitive_data.date_of_birth, date(1990, 5, 15))

    def test_encrypted_fields(self):
        """Test encrypted field properties with real Fernet encryption"""
        # Create a fixed key for testing
        test_key = Fernet.generate_key()
        fernet = Fernet(test_key)

        # Patch _get_fernet to return our fixed Fernet instance
        with patch("core.utils.encryption._get_fernet", return_value=fernet):
            sensitive_data = PersonSensitiveData.objects.create(
                fpl_member=self.fpl_member,
                date_of_birth=date(1990, 5, 15),
                blood_type="A+",
            )

            # Test bank account encryption/decryption
            test_account = "1234567890"
            sensitive_data.bank_account = test_account
            sensitive_data.save()

            # Reload from database
            sensitive_data.refresh_from_db()
            self.assertEqual(sensitive_data.bank_account, test_account)

            # Test PAN number encryption/decryption
            test_pan = "ABCDE1234F"
            sensitive_data.pan_number = test_pan
            sensitive_data.save()

            sensitive_data.refresh_from_db()
            self.assertEqual(sensitive_data.pan_number, test_pan)

            # directly verify that stored values are bytes (encrypted)
            raw_bank = sensitive_data._bank_account  # underlying field
            raw_pan = sensitive_data._pan_number
            self.assertIsInstance(raw_bank, bytes)
            self.assertIsInstance(raw_pan, bytes)
            self.assertNotEqual(raw_bank, test_account.encode())
            self.assertNotEqual(raw_pan, test_pan.encode())

    def test_blood_compatibility(self):
        """Test blood donation and receiving compatibility"""
        sensitive_data = PersonSensitiveData.objects.create(
            fpl_member=self.fpl_member,
            date_of_birth=date(1990, 5, 15),
            blood_type="O-",  # Universal donor
        )

        # O- can donate to all blood types
        expected_donations = ["O-", "O+", "A+", "A-", "B+", "B-", "AB+", "AB-"]
        self.assertEqual(set(sensitive_data.can_donate_to), set(expected_donations))

        # O- can only receive from O-
        self.assertEqual(sensitive_data.can_receive_from, ["O-"])

    def test_ab_positive_compatibility(self):
        """Test AB+ blood type (universal receiver)"""
        sensitive_data = PersonSensitiveData.objects.create(
            fpl_member=self.fpl_member,
            date_of_birth=date(1990, 5, 15),
            blood_type="AB+",
        )

        # AB+ can only donate to AB+
        self.assertEqual(sensitive_data.can_donate_to, ["AB+"])

        # AB+ can receive from all blood types
        expected_receives = ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]
        self.assertEqual(set(sensitive_data.can_receive_from), set(expected_receives))

    def test_sensitive_data_str(self):
        """Test sensitive data string representation"""
        sensitive_data = PersonSensitiveData.objects.create(
            fpl_member=self.fpl_member, date_of_birth=date(1990, 5, 15), blood_type="A+"
        )

        str_repr = str(sensitive_data)
        self.assertIn("John Doe", str_repr)
        self.assertIn("A+", str_repr)
        self.assertIn("Sensitive Data", str_repr)

    def test_encrypted_fields_with_none(self):
        """Test encrypted fields handle None values"""
        sensitive_data = PersonSensitiveData.objects.create(
            fpl_member=self.fpl_member, date_of_birth=date(1990, 5, 15), blood_type="B+"
        )

        # Test None values
        sensitive_data.bank_account = None
        sensitive_data.pan_number = None
        sensitive_data.save()

        sensitive_data.refresh_from_db()
        self.assertIsNone(sensitive_data.bank_account)
        self.assertIsNone(sensitive_data.pan_number)


class PersonEducationModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        # self.role = Role.objects.create(name="Member", description="Member role")  # TODO: Uncomment when Role model is ready
        self.person = Person.objects.create(
            first_name="Alice",
            last_name="Johnson",
            role="Member",  # TODO: Change back to role=self.role when Role model is ready
        )
        self.palika = Palika.objects.create(palika="Latipur", short_name="LTT")
        self.fpl_member = FPLMember.objects.create(
            person=self.person, palika=self.palika, start_date=date(2023, 1, 1)
        )

    def test_education_creation(self):
        """Test education record creation"""
        education = PersonEducation.objects.create(
            fpl_member=self.fpl_member,
            level="BA",
            institution="Test University",
            field_of_study="Computer Science",
        )
        self.assertEqual(education.fpl_member, self.fpl_member)
        self.assertEqual(education.level, "BA")
        self.assertEqual(education.institution, "Test University")
        self.assertEqual(education.field_of_study, "Computer Science")
        self.assertFalse(education.is_current)  # Default value

    def test_education_str(self):
        """Test education string representation"""
        education = PersonEducation.objects.create(
            fpl_member=self.fpl_member,
            level="MA",
            institution="Graduate School",
            is_current=True,
        )
        expected_str = "Master's at Graduate School [Currently studying: True]"
        self.assertEqual(str(education), expected_str)

    def test_education_default_values(self):
        """Test education default values"""
        education = PersonEducation.objects.create(
            fpl_member=self.fpl_member, level="PHD"
        )
        self.assertEqual(education.institution, "")
        self.assertEqual(education.field_of_study, "")
        self.assertFalse(education.is_current)

    def test_education_choices(self):
        """Test education level choices"""
        valid_levels = ["SCHOOL", "PLUS_TWO", "BA", "MA", "PHD", "OTHER"]

        for level in valid_levels:
            education = PersonEducation.objects.create(
                fpl_member=self.fpl_member, level=level
            )
            self.assertEqual(education.level, level)
            # Clean up for next iteration
            education.delete()

    def test_one_to_one_education_relationship(self):
        """Test that FPL member can only have one education record"""
        PersonEducation.objects.create(fpl_member=self.fpl_member, level="BA")

        # Creating another education record for same member should fail
        with self.assertRaises(IntegrityError):
            PersonEducation.objects.create(fpl_member=self.fpl_member, level="MA")


class ModelsIntegrationTest(TestCase):
    """Integration tests for all models working together"""

    def setUp(self):
        """Set up complete test data"""
        # self.role = Role.objects.create(name="Volunteer", description="Volunteer role")  # TODO: Uncomment when Role model is ready
        self.palika = Palika.objects.create(palika="Latipur", short_name="LTT")
        self.contact = Contact.objects.create(
            phone_number="9876543210", email="integration@test.com"
        )

    def test_complete_person_workflow(self):
        """Test creating a person with all related models"""
        key = Fernet.generate_key()
        with patch("core.utils.encryption._get_fernet", return_value=Fernet(key)):
            # Create person
            person = Person.objects.create(
                first_name="Complete",
                last_name="Test",
                role="Volunteer",  # TODO: Change back to role=self.role when Role model is ready
                contact=self.contact,
                bio="Integration test person",
                gender="F",
            )

            # Create FPL member
            fpl_member = FPLMember.objects.create(
                person=person,
                palika=self.palika,
                start_date=date(2023, 6, 1),
                agreement=True,
            )

            # Create sensitive data
            sensitive_data = PersonSensitiveData.objects.create(
                fpl_member=fpl_member, date_of_birth=date(1995, 8, 20), blood_type="AB-"
            )
            sensitive_data.bank_account = "9876543210123456"
            sensitive_data.pan_number = "ZYXWV9876E"
            sensitive_data.save()

            # Create education record
            education = PersonEducation.objects.create(
                fpl_member=fpl_member,
                level="MA",
                institution="Integration University",
                field_of_study="Development Studies",
                is_current=False,
            )

            # Test all relationships work
            self.assertEqual(person.fpl_member, fpl_member)
            self.assertEqual(fpl_member.personsensitivedata, sensitive_data)
            self.assertEqual(fpl_member.education, education)

            # Test encrypted data
            self.assertEqual(sensitive_data.bank_account, "9876543210123456")
            self.assertEqual(sensitive_data.pan_number, "ZYXWV9876E")

            # Test blood compatibility
            self.assertEqual(sensitive_data.can_donate_to, ["AB-", "AB+"])
            expected_receive = ["O-", "A-", "B-", "AB-"]
            self.assertEqual(
                set(sensitive_data.can_receive_from), set(expected_receive)
            )
