from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from core.models import Palika, OrganizationType, SchoolType, Class, Weekday


class PalikaModelTest(TestCase):
    """Test cases for Palika model"""

    def test_palika_creation(self):
        """Test successful palika creation with fresh data"""
        palika = Palika.objects.create(palika="NewTown", short_name="ntw")
        self.assertEqual(palika.palika, "NewTown")
        self.assertEqual(palika.short_name, "ntw")
        self.assertEqual(str(palika), "Newtown (NTW)")

    def test_palika_unique_palika(self):
        """Test that palika names must be unique (seeded data already has Lalitpur)"""
        with self.assertRaises(IntegrityError):
            Palika.objects.create(palika="Laltipur", short_name="lal99")

    def test_palika_unique_short_name(self):
        """Test that short names must be unique (seeded data already has ltt)"""
        with self.assertRaises(IntegrityError):
            Palika.objects.create(palika="AnotherTown", short_name="ltt")

    def test_palika_max_lengths(self):
        """Test field length constraints using full_clean"""
        # palika > 100 chars
        palika = Palika(palika="A" * 101, short_name="shortx")
        with self.assertRaises(ValidationError):
            palika.full_clean()

        # short_name > 6 chars
        palika = Palika(palika="Somewhere", short_name="B" * 7)
        with self.assertRaises(ValidationError):
            palika.full_clean()

    def test_palika_ordering(self):
        """Test default ordering by palika"""
        Palika.objects.create(palika="ZzzTown", short_name="zzz")
        Palika.objects.create(palika="AaaTown", short_name="aaa")
        palikas = list(Palika.objects.all())
        self.assertEqual(palikas[0].palika, "AaaTown")
        self.assertEqual(palikas[-1].palika, "ZzzTown")

    def test_palika_clean_validation(self):
        """Test custom validation in clean method (short_name must be >= 2 chars)"""
        palika = Palika(palika="Shorty", short_name="x")
        with self.assertRaises(ValidationError):
            palika.full_clean()


class OrganizationTypeModelTest(TestCase):
    """Test cases for OrganizationType model"""

    def test_organization_type_creation(self):
        org_type = OrganizationType.objects.create(name="Federation")
        self.assertEqual(org_type.name, "Federation")
        self.assertEqual(str(org_type), "Federation")

    def test_organization_type_unique(self):
        """Seed already has 'School'"""
        with self.assertRaises(IntegrityError):
            OrganizationType.objects.create(name="School")

    def test_organization_type_ordering(self):
        OrganizationType.objects.create(name="Zoo")
        OrganizationType.objects.create(name="Alpha")
        org_types = list(OrganizationType.objects.all())
        self.assertEqual(org_types[0].name, "Alpha")
        self.assertEqual(org_types[-1].name, "Zoo")

    def test_organization_type_max_length(self):
        org_type = OrganizationType(name="A" * 51)
        with self.assertRaises(ValidationError):
            org_type.full_clean()


class SchoolTypeModelTest(TestCase):
    """Test cases for SchoolType model"""

    def test_school_type_creation(self):
        school_type = SchoolType.objects.create(name="International")
        self.assertEqual(school_type.name, "International")
        self.assertEqual(str(school_type), "International")

    def test_school_type_unique(self):
        """Seed already has 'Public'"""
        with self.assertRaises(IntegrityError):
            SchoolType.objects.create(name="Public")

    def test_school_type_ordering(self):
        SchoolType.objects.create(name="Xtra")
        SchoolType.objects.create(name="AlphaSchool")
        school_types = list(SchoolType.objects.all())
        self.assertEqual(school_types[0].name, "AlphaSchool")
        self.assertEqual(school_types[-1].name, "Xtra")

    def test_school_type_max_length(self):
        school_type = SchoolType(name="B" * 51)
        with self.assertRaises(ValidationError):
            school_type.full_clean()


class ClassModelTest(TestCase):
    """Test cases for Class model"""

    def test_class_creation(self):
        """Use a class_number outside the seeded 1–10 range"""
        class_obj = Class.objects.create(class_number=99)
        self.assertEqual(class_obj.class_number, 99)
        self.assertEqual(str(class_obj), "Class 99")

    def test_class_unique(self):
        """Seed already has Class 1"""
        with self.assertRaises(IntegrityError):
            Class.objects.create(class_number=1)

    def test_class_positive_integer(self):
        """Test that class_number accepts positive integers"""
        class_obj = Class.objects.create(class_number=50)
        self.assertEqual(class_obj.class_number, 50)

    def test_class_ordering(self):
        """Ordering is by class_number; seed already has 1–10"""
        classes = list(Class.objects.all())
        self.assertEqual(classes[0].class_number, 1)
        self.assertEqual(classes[-1].class_number, 10)


class WeekdayModelTest(TestCase):
    """Test cases for Weekday model"""

    def test_weekday_creation(self):
        weekday = Weekday.objects.create(name="Funday")
        self.assertEqual(weekday.name, "Funday")
        self.assertEqual(str(weekday), "Funday")

    def test_weekday_unique(self):
        """Seed already has 'Friday'"""
        with self.assertRaises(IntegrityError):
            Weekday.objects.create(name="Friday")

    def test_weekday_max_length(self):
        weekday = Weekday(name="C" * 11)
        with self.assertRaises(ValidationError):
            weekday.full_clean()

    def test_weekday_ordering(self):
        """Weekdays are ordered by pk (insertion order)"""
        existing = list(Weekday.objects.all())
        self.assertTrue(all(isinstance(w, Weekday) for w in existing))
        self.assertEqual(existing[0].pk, 1)  # Monday should be first
