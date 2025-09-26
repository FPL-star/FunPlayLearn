import os
from django.test import TestCase, Client
from django.db import IntegrityError
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date
from unittest.mock import patch
from cryptography.fernet import Fernet

from people.models import (
    Person,
    FPLMember,
    PersonSensitiveData,
    PersonEducation,
    PersonContact,
)
from core.models import Palika, Contact
from organizations.models import (
    Role,
    Organization,
    OrganizationContact,
    OrganizationType,
)


class BaseModelTest(TestCase):
    """Helper base class to provide common seeded setup."""

    def setUp(self):
        os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
        self.palika, _ = Palika.objects.get_or_create(
            palika="Lalitpur", defaults={"short_name": "ltt"}
        )
        self.org_type, _ = OrganizationType.objects.get_or_create(name="FPL")
        self.org_contact, _ = Contact.objects.get_or_create(
            email="org@test.com", defaults={"is_organization": True}
        )
        self.organization, _ = Organization.objects.get_or_create(
            name="FunPlayLearn",
            defaults={
                "palika": self.palika,
                "contact": self.org_contact,
                "org_type": self.org_type,
            },
        )
        self.role, _ = Role.objects.get_or_create(
            name="Test Role", organization=self.organization
        )
        self.user, _ = User.objects.get_or_create(
            username="test_user", defaults={"email": "user@test.com"}
        )
        self.person, _ = Person.objects.get_or_create(
            first_name="Test", last_name="Person", defaults={"role": self.role}
        )
        self.member, _ = FPLMember.objects.get_or_create(
            person=self.person,
            defaults={
                "user": self.user,
                "palika": self.palika,
                "start_date": date(2023, 1, 1),
                "active": True,
            },
        )


class PersonModelTest(BaseModelTest):
    def test_person_creation_str(self):
        person = Person.objects.create(
            first_name="John", last_name="Doe", role=self.role
        )
        expected = f"John Doe"
        self.assertEqual(str(person), expected)

    def test_person_defaults(self):
        person = Person.objects.create(
            first_name="Alice", last_name="Smith", role=self.role
        )
        self.assertEqual(person.gender, "N")
        self.assertEqual(person.bio, "")
        self.assertIsNone(person.contact)

    def test_person_sensitive_data_encryption(self):
        key = Fernet.generate_key()
        fernet = Fernet(key)
        with patch("core.utils.encryption._get_fernet", return_value=fernet):
            sensitive = PersonSensitiveData.objects.create(
                fpl_member=self.member, date_of_birth=date(1990, 5, 15), blood_type="A+"
            )
            sensitive.bank_account = "1234567890"
            sensitive.save()
            sensitive.refresh_from_db()
            self.assertEqual(sensitive.bank_account, "1234567890")
            self.assertIn("AB+", sensitive.can_donate_to)
            self.assertIn("A-", sensitive.can_receive_from)


class FPLMemberModelTest(BaseModelTest):
    def setUp(self):
        super().setUp()
        self.person = Person.objects.create(
            first_name="John", last_name="Doe", role=self.role
        )
        self.user = User.objects.create(username="fpl_test_user")

    def test_fpl_member_creation_defaults(self):
        member = FPLMember.objects.create(
            person=self.person,
            user=self.user,
            palika=self.palika,
            start_date=date(2023, 1, 1),
        )
        self.assertTrue(member.active)
        self.assertFalse(member.sim_returned)

    def test_fpl_member_str(self):
        member = FPLMember.objects.create(
            person=self.person,
            user=self.user,
            palika=self.palika,
            start_date=date(2023, 1, 1),
        )
        self.assertEqual(str(member), f"{self.person.full_name} [Active: True]")

    def test_fpl_member_one_to_one(self):
        fresh_person = Person.objects.create(
            first_name="Fresh", last_name="Person", role=self.role
        )
        fresh_user = User.objects.create(username="freshuser")
        FPLMember.objects.create(
            person=fresh_person,
            user=fresh_user,
            palika=self.palika,
            start_date=date(2023, 1, 1),
        )
        with self.assertRaises(IntegrityError):
            FPLMember.objects.create(
                person=fresh_person,
                user=fresh_user,
                palika=self.palika,
                start_date=date(2023, 2, 1),
            )


class PersonSensitiveDataModelTest(BaseModelTest):
    def test_sensitive_data_creation(self):
        data = PersonSensitiveData.objects.create(
            fpl_member=self.member, date_of_birth=date(1990, 5, 15), blood_type="O+"
        )
        self.assertEqual(data.blood_type, "O+")

    def test_encrypted_fields_with_patch(self):
        key = Fernet.generate_key()
        fernet = Fernet(key)
        with patch("core.utils.encryption._get_fernet", return_value=fernet):
            data = PersonSensitiveData.objects.create(
                fpl_member=self.member, date_of_birth=date(1990, 5, 15), blood_type="A+"
            )
            data.bank_account = "1234567890"
            data.pan_number = "ABCDE1234F"
            data.save()
            data.refresh_from_db()
            self.assertEqual(data.bank_account, "1234567890")
            self.assertEqual(data.pan_number, "ABCDE1234F")
            self.assertIsInstance(data._bank_account, bytes)
            self.assertIsInstance(data._pan_number, bytes)

    def test_blood_compatibility(self):
        sensitive_data = PersonSensitiveData.objects.create(
            fpl_member=self.member,
            blood_type="A+",
            date_of_birth=date(1990, 5, 15),
        )
        self.assertEqual(sensitive_data.can_donate_to, ["A+", "AB+"])
        self.assertEqual(sensitive_data.can_receive_from, ["O-", "O+", "A-", "A+"])

    def test_ab_positive_universal_receiver(self):
        data = PersonSensitiveData.objects.create(
            fpl_member=self.member, date_of_birth=date(1990, 5, 15), blood_type="AB+"
        )
        self.assertEqual(data.can_donate_to, ["AB+"])
        self.assertIn("O-", data.can_receive_from)

    def test_sensitive_data_str(self):
        data = PersonSensitiveData.objects.create(
            fpl_member=self.member, date_of_birth=date(1990, 5, 15), blood_type="A+"
        )
        self.assertIn("Test Person", str(data))

    def test_encrypted_fields_with_none(self):
        data = PersonSensitiveData.objects.create(
            fpl_member=self.member, date_of_birth=date(1990, 5, 15), blood_type="B+"
        )
        data.bank_account = None
        data.pan_number = None
        data.save()
        data.refresh_from_db()
        self.assertIsNone(data.bank_account)
        self.assertIsNone(data.pan_number)


class PersonEducationModelTest(BaseModelTest):
    def test_education_creation(self):
        edu = PersonEducation.objects.create(
            fpl_member=self.member,
            level="BA",
            institution="Test University",
            field_of_study="CS",
        )
        self.assertEqual(edu.level, "BA")

    def test_education_str(self):
        edu = PersonEducation.objects.create(
            fpl_member=self.member,
            level="MA",
            institution="Grad School",
            is_current=True,
        )
        self.assertIn("Grad School", str(edu))

    def test_defaults(self):
        edu = PersonEducation.objects.create(fpl_member=self.member, level="PHD")
        self.assertEqual(edu.institution, "")
        self.assertFalse(edu.is_current)

    def test_level_choices(self):
        valid_levels = ["SCHOOL", "PLUS_TWO", "BA", "MA", "PHD", "OTHER"]
        for lvl in valid_levels:
            edu = PersonEducation.objects.create(fpl_member=self.member, level=lvl)
            self.assertEqual(edu.level, lvl)
            edu.delete()

    def test_one_to_one_constraint(self):
        PersonEducation.objects.create(fpl_member=self.member, level="BA")
        with self.assertRaises(IntegrityError):
            PersonEducation.objects.create(fpl_member=self.member, level="MA")


class FPLMemberAdminTests(BaseModelTest):
    def setUp(self):
        super().setUp()
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="adminpassword",
        )
        self.client.force_login(self.superuser)
        self.org_type_fpl, _ = OrganizationType.objects.get_or_create(name="FPL")
        self.contact_org, _ = Contact.objects.get_or_create(
            email="org@funplaylearn.com", defaults={"is_organization": True}
        )
        self.org_fpl, _ = Organization.objects.get_or_create(
            name="FunPlayLearn",
            defaults={
                "org_type": self.org_type_fpl,
                "contact": self.contact_org,
            },
        )
        self.role_fellow, _ = Role.objects.get_or_create(
            name="Fellow", organization=self.org_fpl
        )
        self.role_teacher, _ = Role.objects.get_or_create(
            name="Teacher", organization=self.org_fpl
        )
        self.palika_lalitpur, _ = Palika.objects.get_or_create(
            palika="Lalitpur", defaults={"short_name": "ltt"}
        )
        self.palika_hetauda, _ = Palika.objects.get_or_create(
            palika="Hetauda", defaults={"short_name": "htd"}
        )

        self.add_url = reverse("admin:people_fplmember_add")
        self.list_url = reverse("admin:people_fplmember_changelist")

    def test_fplmember_add_view_initial_form(self):
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/change_form.html")

    def test_fplmember_create_success(self):
        data = {
            "palika": self.palika_lalitpur.pk,
            "start_date": "2023-01-01",
            "active": True,
            "agreement": "on",
            "first_name": "John",
            "last_name": "Doe",
            "gender": "M",
            "role": self.role_fellow.pk,
            "email": "john.doe.create@funplaylearn.org",
            "date_of_birth": "1990-05-15",
            "blood_type": "A+",
        }
        response = self.client.post(self.add_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.list_url)

    def test_fplmember_create_fails_without_required_fields(self):
        data = {
            "palika": self.palika_hetauda.pk,
            "start_date": "2023-01-01",
            "active": True,
            "agreement": True,
            "first_name": "Jane",
            "last_name": "Smith",
            "gender": "F",
            "role": self.role_teacher.pk,
            "email": "jane.smith@funplaylearn.org",
            "blood_type": "B-",
            # 'date_of_birth' is intentionally omitted
        }

        response = self.client.post(self.add_url, data)
        self.assertContains(response, "This field is required.", count=1)
        self.assertFalse(FPLMember.objects.filter(person__first_name="Jane").exists())

    def test_fplmember_update_success(self):

        user, _ = User.objects.get_or_create(
            username="test.user@funplaylearn.org",
            defaults={"first_name": "Test", "last_name": "User"},
        )
        contact, _ = PersonContact.objects.get_or_create(
            email="test.user@funplaylearn.org"
        )
        person, _ = Person.objects.get_or_create(
            first_name="Test",
            last_name="User",
            defaults={"contact": contact, "role": self.role_fellow},
        )
        fpl_member, _ = FPLMember.objects.get_or_create(
            person=person,
            defaults={
                "user": user,
                "palika": self.palika_lalitpur,
                "start_date": "2022-01-01",
                "active": True,
                "agreement": True,
            },
        )
        sensitive_data, _ = PersonSensitiveData.objects.get_or_create(
            fpl_member=fpl_member,
            defaults={"blood_type": "O-", "date_of_birth": "2000-01-01"},
        )
        education, _ = PersonEducation.objects.get_or_create(
            fpl_member=fpl_member, defaults={"level": "MA"}
        )

        edit_url = reverse("admin:people_fplmember_change", args=[fpl_member.pk])

        updated_data = {
            "palika": self.palika_hetauda.pk,
            "start_date": "2022-01-01",
            "active": False,
            "agreement": False,
            "leave_date": "2024-05-01",
            "first_name": "Updated",
            "last_name": "Name",
            "gender": "F",
            "role": self.role_teacher.pk,
            "bio": "Updated bio.",
            "email": "updated.name@funplaylearn.org",
            "phone_country_code": "977",
            "phone_number": "9876543210",
            "address": "Pokhara, Nepal",
            "emergency_contact_name": "New Contact",
            "emergency_contact_phone": "9810987654",
            "emergency_contact_relationship": "Parent",
            "date_of_birth": "2000-02-02",
            "blood_type": "AB+",
            "bank_account": "1122334455",
            "pan_number": "NEWPAN",
            "edu_level": "MA",
            "edu_institution": "New University",
            "edu_field_of_study": "Science",
            "is_current_edu": False,
        }

        response = self.client.post(edit_url, updated_data, follow=True)

        self.assertRedirects(response, self.list_url)
        self.assertEqual(response.status_code, 200)

        fpl_member.refresh_from_db()
        person.refresh_from_db()
        user.refresh_from_db()
        contact.refresh_from_db()
        sensitive_data.refresh_from_db()
        education.refresh_from_db()

        self.assertEqual(fpl_member.palika, self.palika_hetauda)
        self.assertFalse(fpl_member.active)
        self.assertEqual(fpl_member.leave_date.strftime("%Y-%m-%d"), "2024-05-01")
        self.assertEqual(user.first_name, "Updated")
        self.assertEqual(user.last_name, "Name")
        self.assertEqual(user.email, "updated.name@funplaylearn.org")
        self.assertEqual(person.first_name, "Updated")
        self.assertEqual(person.last_name, "Name")
        self.assertEqual(person.bio, "Updated bio.")
        self.assertEqual(contact.email, "updated.name@funplaylearn.org")
        self.assertEqual(contact.address, "Pokhara, Nepal")
        self.assertEqual(sensitive_data.blood_type, "AB+")
        self.assertEqual(str(sensitive_data.date_of_birth), "2000-02-02")
        self.assertEqual(education.level, "MA")
        self.assertEqual(education.institution, "New University")
