from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.utils import DataError
from taxonomy.models import Palika, OrganizationType, SchoolType, Class, Weekday


class PalikaModelTest(TestCase):
    """Test cases for Palika model"""

    def setUp(self):
        self.palika_data = {"palika": "Lalitpur", "short_name": "LTT"}

    def test_palika_creation(self):
        """Test successful palika creation"""
        palika = Palika.objects.create(**self.palika_data)
        self.assertEqual(palika.palika, "Lalitpur")
        self.assertEqual(palika.short_name, "LTT")
        self.assertEqual(str(palika), "Lalitpur (LTT)")

    def test_palika_unique_palika(self):
        """Test that palika names must be unique"""
        Palika.objects.create(**self.palika_data)
        with self.assertRaises(IntegrityError):
            Palika.objects.create(
                palika="Lalitpur", short_name="LAL"  # Duplicate palika
            )

    def test_palika_unique_short_name(self):
        """Test that short names must be unique"""
        Palika.objects.create(**self.palika_data)
        with self.assertRaises(IntegrityError):
            Palika.objects.create(
                palika="Kathmandu", short_name="LTT"
            )  # Duplicate short_name

    def test_palika_max_lengths(self):
        """
        Test field length constraints
        The test uses full_clean() rather than checking for DataErrors because
        some SQL backends (such as SQLite) do not raise DataError at the DB level
        despite having a max_length arg in the model definition.
        """
        # Test palika max length (100 chars)
        palika_field = "A" * 101
        palika = Palika.objects.create(palika=palika_field, short_name="TST")
        with self.assertRaises(ValidationError):
            palika.full_clean()

        # Test short_name max length (6 chars)
        short_name_field = "A" * 7
        palika = Palika.objects.create(palika="Test", short_name=short_name_field)
        with self.assertRaises(ValidationError):
            palika.full_clean()

    def test_palika_ordering(self):
        """Test default ordering by palika"""
        Palika.objects.create(palika="Zebra", short_name="ZEB")
        Palika.objects.create(palika="Alpha", short_name="ALP")
        palikas = list(Palika.objects.all())
        self.assertEqual(palikas[0].palika, "Alpha")
        self.assertEqual(palikas[1].palika, "Zebra")

    def test_palika_clean_validation(self):
        """Test custom validation in clean method"""
        palika = Palika(palika="Test", short_name="T")
        with self.assertRaises(ValidationError):
            palika.full_clean()


class OrganizationTypeModelTest(TestCase):
    """Test cases for OrganizationType model"""

    def test_organization_type_creation(self):
        """Test successful organization type creation"""
        org_type = OrganizationType.objects.create(name="School")
        self.assertEqual(org_type.name, "School")
        self.assertEqual(str(org_type), "School")

    def test_organization_type_unique(self):
        """Test that organization types must be unique"""
        OrganizationType.objects.create(name="School")

        with self.assertRaises(IntegrityError):
            OrganizationType.objects.create(name="School")

    def test_organization_type_ordering(self):
        """Test default ordering by name"""
        OrganizationType.objects.create(name="School")
        OrganizationType.objects.create(name="College")
        OrganizationType.objects.create(name="NGO")

        org_types = list(OrganizationType.objects.all())
        self.assertEqual(org_types[0].name, "College")
        self.assertEqual(org_types[1].name, "NGO")
        self.assertEqual(org_types[2].name, "School")

    def test_organization_type_max_length(self):
        """Test field length constraints"""
        # Test name max length (50 chars)
        long_name = "A" * 51
        org_type = OrganizationType.objects.create(name=long_name)
        with self.assertRaises(ValidationError):
            org_type.full_clean()


class SchoolTypeModelTest(TestCase):
    """Test cases for SchoolType model"""

    def test_school_type_creation(self):
        """Test successful school type creation"""
        school_type = SchoolType.objects.create(name="Private")
        self.assertEqual(school_type.name, "Private")
        self.assertEqual(str(school_type), "Private")

    def test_school_type_unique(self):
        """Test that school types must be unique"""
        SchoolType.objects.create(name="Public")

        with self.assertRaises(IntegrityError):
            SchoolType.objects.create(name="Public")

    def test_school_type_ordering(self):
        """Test default ordering by name"""
        SchoolType.objects.create(name="Public")
        SchoolType.objects.create(name="Community")
        SchoolType.objects.create(name="Private")

        school_types = list(SchoolType.objects.all())
        self.assertEqual(school_types[0].name, "Community")
        self.assertEqual(school_types[1].name, "Private")
        self.assertEqual(school_types[2].name, "Public")

    def test_school_type_max_length(self):
        """Test field length constraints"""
        # Test name max length (50 chars)
        long_name = "A" * 51
        school_type = SchoolType.objects.create(name=long_name)
        with self.assertRaises(ValidationError):
            school_type.full_clean()


class ClassModelTest(TestCase):
    """Test cases for Class model"""

    def test_class_creation(self):
        """Test successful class creation"""
        class_obj = Class.objects.create(class_number=5)
        self.assertEqual(class_obj.class_number, 5)
        self.assertEqual(str(class_obj), "Class 5")

    def test_class_unique(self):
        """Test that class numbers must be unique"""
        Class.objects.create(class_number=1)

        with self.assertRaises(IntegrityError):
            Class.objects.create(class_number=1)

    def test_class_positive_integer(self):
        """Test that class_number accepts positive integers"""
        # Valid positive integers
        for i in range(1, 11):
            class_obj = Class.objects.create(class_number=i)
            self.assertEqual(class_obj.class_number, i)

    def test_class_ordering(self):
        """Test classes are ordered by class_number"""
        Class.objects.create(class_number=10)
        Class.objects.create(class_number=1)
        Class.objects.create(class_number=5)

        classes = list(Class.objects.all())
        self.assertEqual(classes[0].class_number, 1)
        self.assertEqual(classes[1].class_number, 5)
        self.assertEqual(classes[2].class_number, 10)


class WeekdayModelTest(TestCase):
    """Test cases for Weekday model"""

    def test_weekday_creation(self):
        """Test successful weekday creation"""
        weekday = Weekday.objects.create(name="Monday")
        self.assertEqual(weekday.name, "Monday")
        self.assertEqual(str(weekday), "Monday")

    def test_weekday_unique(self):
        """Test that weekday names must be unique"""
        Weekday.objects.create(name="Friday")

        with self.assertRaises(IntegrityError):
            Weekday.objects.create(name="Friday")

    def test_weekday_max_length(self):
        """Test field length constraints"""
        # Test name max length (10 chars)
        long_name = "A" * 11
        weekday = Weekday.objects.create(name=long_name)
        with self.assertRaises(ValidationError):
            weekday.full_clean()

    def test_weekday_ordering(self):
        """Test weekdays are ordered by pk (insertion order)"""
        monday = Weekday.objects.create(name="Monday")
        friday = Weekday.objects.create(name="Friday")
        tuesday = Weekday.objects.create(name="Tuesday")

        weekdays = list(Weekday.objects.all())
        # Should be ordered by pk (insertion order)
        self.assertEqual(weekdays[0], monday)
        self.assertEqual(weekdays[1], friday)
        self.assertEqual(weekdays[2], tuesday)
