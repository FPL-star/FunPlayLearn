# organizations/migrations/0002_seed_funplaylearn.py
from django.db import migrations


def create_funplaylearn_org(apps, schema_editor):
    Contact = apps.get_model("core", "Contact")
    Organization = apps.get_model("organizations", "Organization")
    OrganizationType = apps.get_model("core", "OrganizationType")
    Role = apps.get_model("organizations", "Role")

    # --- Create Contact for FunPlayLearn ---
    contact, _ = Contact.objects.get_or_create(
        email="admin@funplaylearn.org",
        defaults={
            "phone_country_code": "977",
            "phone_number": "99999999",
            "is_organization": True,
        },
    )

    # --- Get FPL organization type ---
    fpl_type = OrganizationType.objects.get(name="FPL")

    # --- Create Organization ---
    org, _ = Organization.objects.get_or_create(
        name="FunPlayLearn",
        org_type=fpl_type,
        contact=contact,
    )

    # --- Create Roles for FunPlayLearn ---
    fpl_roles = ["Fellow", "Intern", "Fulltime", "Executive", "Board", "Alumni"]

    for role_name in sorted(fpl_roles):
        Role.objects.get_or_create(name=role_name, organization=org)


def reverse_funplaylearn_org(apps, schema_editor):
    Organization = apps.get_model("organizations", "Organization")
    Role = apps.get_model("organizations", "Role")
    Contact = apps.get_model("core", "Contact")

    # Delete Roles
    org = Organization.objects.filter(name="FunPlayLearn").first()
    if org:
        Role.objects.filter(organization=org).delete()
        org.delete()

    # Delete Contact if it exists
    Contact.objects.filter(email="admin@funplaylearn.org").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("organizations", "0001_initial"),
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            create_funplaylearn_org,
            reverse_funplaylearn_org,
        ),
    ]
