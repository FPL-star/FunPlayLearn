from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.utils import DataError
from taxonomy.models import Palika, OrganizationType, SchoolType, Class, Weekday


class PalikaModelTest(TestCase):
    """Test cases for Palika model"""

    def setUp(self):
        self.palika_data = {"name": "Lalitpur", "abbreviated_name": "LTT"}

    def test_palika_creation(self):
        """Test successful palika creation"""
        palika = Palika.objects.create(**self.palika_data)
        self.assertEqual(palika.name, "Lalitpur")
        self.assertEqual(palika.abbreviated_name, "LTT")
        self.assertEqual(str(palika), "Lalitpur (LTT)")

    def test_palika_unique_name(self):
        """Test that palika names must be unique"""
        Palika.objects.create(**self.palika_data)

        with self.assertRaises(IntegrityError):
            Palika.objects.create(
                name="Lalitpur", abbreviated_name="LAL"  # Duplicate name
            )

    def test_palika_unique_abbreviated_name(self):
        """Test that abbreviated names must be unique"""
        Palika.objects.create(**self.palika_data)

        with self.assertRaises(IntegrityError):
            Palika.objects.create(
                name="Kathmandu", abbreviated_name="LTT"  # Duplicate abbreviated name
            )

    def test_palika_max_lengths(self):
        """
        Test field length constraints
        The test uses full_clean() rather than checking for DataErrors because
        some SQL backends (such as SQLite) do not raise DataError at the DB level
        despite having a max_length arg in the model definition.
        """
        # Test name max length (100 chars)
        long_name = "A" * 101
        palika = Palika.objects.create(name=long_name, abbreviated_name="TST")
        with self.assertRaises(ValidationError):
            palika.full_clean()

        # Test abbreviated_name max length (6 chars)
        long_abbrev = "TOOLONG"
        palika = Palika.objects.create(name="Test", abbreviated_name=long_abbrev)
        with self.assertRaises(ValidationError):
            palika.full_clean()

    def test_palika_ordering(self):
        """Test default ordering by name"""
        Palika.objects.create(name="Zebra", abbreviated_name="ZEB")
        Palika.objects.create(name="Alpha", abbreviated_name="ALP")

        palikas = list(Palika.objects.all())
        self.assertEqual(palikas[0].name, "Alpha")
        self.assertEqual(palikas[1].name, "Zebra")

    def test_palika_clean_validation(self):
        """Test custom validation in clean method"""
        palika = Palika(name="Test", abbreviated_name="T")
        with self.assertRaises(ValidationError):
            palika.full_clean()


class OrganizationTypeModelTest(TestCase):
    """Test cases for OrganizationType model"""

    def test_organization_type_creation(self):
        """Test successful organization type creation"""
        org_type = OrganizationType.objects.create(
            type=OrganizationType.OrganizationChoices.SCHOOL
        )
        self.assertEqual(org_type.type, "school")
        self.assertEqual(str(org_type), "School")  # Display value

    def test_organization_type_choices(self):
        """Test that only valid choices are accepted"""
        # Valid choice
        org_type = OrganizationType.objects.create(
            type=OrganizationType.OrganizationChoices.NGO
        )
        self.assertEqual(org_type.type, "ngo")

    def test_organization_type_unique(self):
        """Test that organization types must be unique"""
        OrganizationType.objects.create(
            type=OrganizationType.OrganizationChoices.SCHOOL
        )

        with self.assertRaises(IntegrityError):
            OrganizationType.objects.create(
                type=OrganizationType.OrganizationChoices.SCHOOL
            )

    def test_organization_type_all_choices_valid(self):
        """Test all defined choices can be created"""
        choices = OrganizationType.OrganizationChoices

        for choice_value, choice_label in choices.choices:
            org_type = OrganizationType.objects.create(type=choice_value)
            self.assertEqual(org_type.get_type_display(), choice_label)


class SchoolTypeModelTest(TestCase):
    """Test cases for SchoolType model"""

    def test_school_type_creation(self):
        """Test successful school type creation"""
        school_type = SchoolType.objects.create(type=SchoolType.SchoolChoices.PRIVATE)
        self.assertEqual(school_type.type, "private")
        self.assertEqual(str(school_type), "Private")

    def test_school_type_unique(self):
        """Test that school types must be unique"""
        SchoolType.objects.create(type=SchoolType.SchoolChoices.PUBLIC)

        with self.assertRaises(IntegrityError):
            SchoolType.objects.create(type=SchoolType.SchoolChoices.PUBLIC)

    def test_all_school_choices_valid(self):
        """Test all defined school choices can be created"""
        choices = SchoolType.SchoolChoices

        for choice_value, choice_label in choices.choices:
            school_type = SchoolType.objects.create(type=choice_value)
            self.assertEqual(school_type.get_type_display(), choice_label)


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

    def test_class_choices_validation(self):
        """Test that only valid class numbers are accepted"""
        # Valid choice
        class_obj = Class.objects.create(class_number=Class.ClassChoices.CLASS_10)
        self.assertEqual(class_obj.class_number, 10)

    def test_all_class_choices_valid(self):
        """Test all defined class choices can be created"""
        choices = Class.ClassChoices

        for choice_value, choice_label in choices.choices:
            class_obj = Class.objects.create(class_number=choice_value)
            self.assertEqual(str(class_obj), choice_label)

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
        weekday = Weekday.objects.create(name=Weekday.DayChoices.MONDAY)
        self.assertEqual(weekday.name, "Monday")
        self.assertEqual(str(weekday), "Monday")

    def test_weekday_unique(self):
        """Test that weekday names must be unique"""
        Weekday.objects.create(name=Weekday.DayChoices.FRIDAY)

        with self.assertRaises(IntegrityError):
            Weekday.objects.create(name=Weekday.DayChoices.FRIDAY)

    def test_all_weekday_choices_valid(self):
        """Test all defined weekday choices can be created"""
        choices = Weekday.DayChoices

        for choice_value, choice_label in choices.choices:
            weekday = Weekday.objects.create(name=choice_value)
            self.assertEqual(weekday.name, choice_label)

    def test_weekday_order_method(self):
        """Test the custom weekday ordering method"""
        # Create weekdays in random order
        Weekday.objects.create(name="Friday")
        Weekday.objects.create(name="Monday")
        Weekday.objects.create(name="Wednesday")
        Weekday.objects.create(name="Sunday")

        ordered_weekdays = list(Weekday.get_weekday_order())
        expected_order = ["Monday", "Wednesday", "Friday", "Sunday"]
        actual_order = [day.name for day in ordered_weekdays]

        self.assertEqual(actual_order, expected_order)


class TaxonomyIntegrationTest(TestCase):
    """Integration tests for taxonomy models"""

    def setUp(self):
        """Set up test data"""
        self.palika = Palika.objects.create(name="Lalitpur", abbreviated_name="LTT")
        self.org_type = OrganizationType.objects.create(
            type=OrganizationType.OrganizationChoices.SCHOOL
        )
        self.school_type = SchoolType.objects.create(
            type=SchoolType.SchoolChoices.PUBLIC
        )
        self.class_obj = Class.objects.create(class_number=5)
        self.weekday = Weekday.objects.create(name=Weekday.DayChoices.MONDAY)

    def test_all_models_created(self):
        """Test that all taxonomy models can be created together"""
        self.assertEqual(Palika.objects.count(), 1)
        self.assertEqual(OrganizationType.objects.count(), 1)
        self.assertEqual(SchoolType.objects.count(), 1)
        self.assertEqual(Class.objects.count(), 1)
        self.assertEqual(Weekday.objects.count(), 1)

    def test_model_string_representations(self):
        """Test all model __str__ methods"""
        self.assertEqual(str(self.palika), "Lalitpur (LTT)")
        self.assertEqual(str(self.org_type), "School")
        self.assertEqual(str(self.school_type), "Public")
        self.assertEqual(str(self.class_obj), "Class 5")
        self.assertEqual(str(self.weekday), "Monday")

    def test_bulk_operations(self):
        """Test bulk creation operations"""
        # Bulk create classes
        classes_data = [
            Class(class_number=i)
            for i in range(1, 11)
            if i != 5  # Skip 5 as it's already created
        ]
        Class.objects.bulk_create(classes_data)
        self.assertEqual(Class.objects.count(), 10)

        # Bulk create weekdays
        weekday_names = [
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        weekdays_data = [Weekday(name=name) for name in weekday_names]
        Weekday.objects.bulk_create(weekdays_data)
        self.assertEqual(Weekday.objects.count(), 7)
