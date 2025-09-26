from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from organizations.forms import OrganizationForm, SchoolForm
from .models import Organization, Role, School, Schoolclass
from core.models import Palika, OrganizationContact, OrganizationType, SchoolType, Class


class SchoolclassTabularInline(admin.TabularInline):
	model=Schoolclass
	fields=("Class","max_students")
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
	form=OrganizationForm
	list_display = ("name", "org_type", "palika", "active")
	list_filter = ("org_type", "palika", "active")
	search_fields = ("name",)
	fieldsets = (
		(
		"Basic Info", {
			"fields": ("name", "org_type", "palika", "active")
		},
		),
		(
		"Location Info", {
			"fields": ("latitude", "longitude", "general_location")
		},
		),
		(
            "Contact Information",
            {
                "fields": ("email", ("phone_country_code", "phone_number"), "address"),
                "classes": ("collapse",),
            },
        ),
	)
@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
	form=SchoolForm
	list_display = ("organization", "school_type", "class_1_fee", "provides_food", "first_session_date")
	list_filter = ("school_type", "provides_food", "organization__palika")
	search_fields = ("organization__name",)
	inlines=[SchoolclassTabularInline]
	fieldsets = (
		
		(
		"Basic Info", {
			"fields": ("school_name", "school_palika", "school_type", "class_1_fee", "provides_food")
		},
		),
		(
		"Session Info", {
			"fields": ("first_session_date", "start_time_firsthalf", "start_time_secondhalf", "session_duration")
		},
		),
		(
			"Contact Information",
			{
				"fields": ("email", ("phone_country_code", "phone_number"), "address"),
				"classes": ("collapse",),
			},
		),
		(
		"Location Info", {
			"fields": ("latitude", "longitude", "general_location")
		},
		),

	)