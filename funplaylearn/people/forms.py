# forms.py
from django import forms
from django.contrib.auth.models import User
from people.models import (
    FPLMember,
    Person,
    PersonEducation,
    PersonSensitiveData,
    PersonContact,
)
from organizations.models import Role, Organization


class FPLMemberForm(forms.ModelForm):

    # --- Basic Information fields
    first_name = forms.CharField(label="First Name")
    last_name = forms.CharField(label="Last Name")
    photo = forms.ImageField(label="Photo", required=False)
    bio = forms.CharField(
        label="Biography", widget=forms.Textarea(attrs={"rows": 3}), required=False
    )

    # --- Organization information
    role = forms.ModelChoiceField(
        label="Role", queryset=Role.objects.filter(organization__name="FunPlayLearn")
    )

    # --- Contact information
    email = forms.EmailField(label="Email Address")
    phone_country_code = forms.CharField(
        label="Country Code",
        initial="977",
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "977"}),
    )
    phone_number = forms.CharField(label="Phone Number", required=False)
    address = forms.CharField(
        label="Address", widget=forms.Textarea(attrs={"rows": 2}), required=False
    )

    # --- Emergency contact information
    emergency_contact_name = forms.CharField(
        label="Emergency Contact Name", required=False
    )
    emergency_contact_phone = forms.CharField(
        label="Emergency Contact Phone", required=False
    )
    emergency_contact_relationship = forms.CharField(
        label="Relationship to Emergency Contact", required=False
    )

    # --- Education information
    edu_level = forms.ChoiceField(
        label="Highest Education Level",
        choices=[("", "--- Select Education Level ---")]
        + PersonEducation.EDUCATION_LEVEL_CHOICES,
        required=False,
    )
    edu_institution = forms.CharField(label="Educational Institution", required=False)
    edu_field_of_study = forms.CharField(label="Field of Study", required=False)
    is_current_edu = forms.BooleanField(label="Currently Enrolled", required=False)

    # --- Medical and Financial information
    blood_type = forms.ChoiceField(
        label="Blood Type",
        choices=[("", "--- Select Blood Type ---")]
        + PersonSensitiveData.BLOOD_TYPE_CHOICES,
        required=True,
    )
    gender = forms.ChoiceField(label="Gender", choices=Person.GENDER_CHOICES)
    date_of_birth = forms.DateField(
        label="Date Of Birth", widget=forms.DateInput(attrs={"type": "date"})
    )
    bank_account = forms.CharField(label="Bank Account Number", required=False)
    pan_number = forms.CharField(label="PAN Number", required=False)

    class Meta:
        model = FPLMember
        fields = [
            "palika",
            "start_date",
            "active",
            "agreement",
            "leave_date",
            "sim_returned",
            "account_closed",
            "certificate_issued",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "leave_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            fpl_member = self.instance

            person = fpl_member.person
            user = fpl_member.user

            # Populate Person fields
            self.fields["first_name"].initial = person.first_name
            self.fields["last_name"].initial = person.last_name
            self.fields["bio"].initial = person.bio
            self.fields["gender"].initial = person.gender
            self.fields["role"].initial = person.role

            # Populate Contact fields
            if hasattr(person, "contact") and person.contact:
                contact = person.contact
                self.fields["email"].initial = contact.email
                self.fields["phone_country_code"].initial = contact.phone_country_code
                self.fields["phone_number"].initial = contact.phone_number
                self.fields["address"].initial = contact.address
                self.fields["emergency_contact_name"].initial = (
                    contact.emergency_contact_name
                )
                self.fields["emergency_contact_phone"].initial = (
                    contact.emergency_contact_phone
                )
                self.fields["emergency_contact_relationship"].initial = (
                    contact.emergency_contact_relationship
                )

            # Populate Sensitive Data fields
            if hasattr(fpl_member, "personsensitivedata"):
                sd = fpl_member.personsensitivedata
                self.fields["date_of_birth"].initial = sd.date_of_birth
                self.fields["blood_type"].initial = sd.blood_type
                self.fields["bank_account"].initial = sd.bank_account
                self.fields["pan_number"].initial = sd.pan_number

            # Populate Education fields
            if hasattr(fpl_member, "education"):
                edu = fpl_member.education
                self.fields["edu_level"].initial = edu.level
                self.fields["edu_institution"].initial = edu.institution
                self.fields["edu_field_of_study"].initial = edu.field_of_study
                self.fields["is_current_edu"].initial = edu.is_current

    def clean(self):
        cleaned_data = super().clean()

        # Validate that first_name and last_name are provided
        first_name = cleaned_data.get("first_name", "").strip()
        last_name = cleaned_data.get("last_name", "").strip()

        if not first_name:
            raise forms.ValidationError("First name is required.")
        if not last_name:
            raise forms.ValidationError("Last name is required.")

        # Auto-generate username for new users
        if not (self.instance and self.instance.pk):
            username = f"{first_name.lower()}.{last_name.lower()}@funplaylearn.org"

            # Check if username already exists
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError(
                    f"A user with the name '{first_name} {last_name}' already exists. "
                    f"Please use a different name or contact an administrator."
                )

        return cleaned_data

    def save(self, commit=True):
        fpl_member = super().save(commit=False)
        cleaned_data = self.cleaned_data

        # Handle User creation/update
        if fpl_member.pk:
            # Update existing user (username doesn't change for existing users)
            user = fpl_member.user
            # No password changes needed - users will use OAuth
            if commit:
                user.save()
        else:
            # Create new user with auto-generated username and random password
            username = f"{cleaned_data['first_name'].lower()}.{cleaned_data['last_name'].lower()}@funplaylearn.org"
            # Generate a secure random password (will be replaced by OAuth later)
            password = User.objects.make_random_password(length=12)

            user = User.objects.create_user(
                username=username,
                password=password,
                email=cleaned_data.get("email", ""),
                first_name=cleaned_data["first_name"],
                last_name=cleaned_data["last_name"],
            )
            fpl_member.user = user

        # Handle Person creation/update
        if fpl_member.pk:
            # Update existing person
            person = fpl_member.person
            person.first_name = cleaned_data["first_name"]
            person.last_name = cleaned_data["last_name"]
            person.bio = cleaned_data.get("bio", "")
            person.gender = cleaned_data["gender"]
            person.role = cleaned_data["role"]
            if cleaned_data.get("photo"):
                person.photo = cleaned_data["photo"]
            if commit:
                person.save()
        else:
            # Create new person with contact
            contact = PersonContact.objects.create(
                email=cleaned_data["email"],
                phone_country_code=cleaned_data.get("phone_country_code", "977"),
                phone_number=cleaned_data.get("phone_number", ""),
                address=cleaned_data.get("address", ""),
                emergency_contact_name=cleaned_data.get("emergency_contact_name", ""),
                emergency_contact_phone=cleaned_data.get("emergency_contact_phone", ""),
                emergency_contact_relationship=cleaned_data.get(
                    "emergency_contact_relationship", ""
                ),
            )
            person = Person.objects.create(
                first_name=cleaned_data["first_name"],
                last_name=cleaned_data["last_name"],
                contact=contact,
                role=cleaned_data["role"],
                bio=cleaned_data.get("bio", ""),
                gender=cleaned_data["gender"],
                photo=cleaned_data.get("photo"),
            )
            fpl_member.person = person

        # Handle Contact updates for existing records
        if (
            fpl_member.pk
            and hasattr(fpl_member.person, "contact")
            and fpl_member.person.contact
        ):
            contact = fpl_member.person.contact
            contact.email = cleaned_data["email"]
            contact.phone_country_code = cleaned_data.get("phone_country_code", "977")
            contact.phone_number = cleaned_data.get("phone_number", "")
            contact.address = cleaned_data.get("address", "")
            contact.emergency_contact_name = cleaned_data.get(
                "emergency_contact_name", ""
            )
            contact.emergency_contact_phone = cleaned_data.get(
                "emergency_contact_phone", ""
            )
            contact.emergency_contact_relationship = cleaned_data.get(
                "emergency_contact_relationship", ""
            )
            if commit:
                contact.save()

        if commit:
            fpl_member.save()

        # Handle PersonSensitiveData creation/update
        if (
            cleaned_data.get("date_of_birth")
            or cleaned_data.get("blood_type")
            or cleaned_data.get("bank_account")
            or cleaned_data.get("pan_number")
        ):
            sensitive_data, created = PersonSensitiveData.objects.get_or_create(
                fpl_member=fpl_member,
                defaults={
                    "date_of_birth": cleaned_data.get("date_of_birth"),
                    "blood_type": cleaned_data.get("blood_type", ""),
                },
            )
            if not created:
                if cleaned_data.get("date_of_birth"):
                    sensitive_data.date_of_birth = cleaned_data["date_of_birth"]
                if cleaned_data.get("blood_type"):
                    sensitive_data.blood_type = cleaned_data["blood_type"]

            # Handle encrypted fields
            if cleaned_data.get("bank_account"):
                sensitive_data.bank_account = cleaned_data["bank_account"]
            if cleaned_data.get("pan_number"):
                sensitive_data.pan_number = cleaned_data["pan_number"]

            if commit:
                sensitive_data.save()

        # Handle PersonEducation creation/update
        if cleaned_data.get("edu_level"):
            education, created = PersonEducation.objects.get_or_create(
                fpl_member=fpl_member,
                defaults={
                    "level": cleaned_data["edu_level"],
                    "institution": cleaned_data.get("edu_institution", ""),
                    "field_of_study": cleaned_data.get("edu_field_of_study", ""),
                    "is_current": cleaned_data.get("is_current_edu", False),
                },
            )
            if not created:
                education.level = cleaned_data["edu_level"]
                education.institution = cleaned_data.get("edu_institution", "")
                education.field_of_study = cleaned_data.get("edu_field_of_study", "")
                education.is_current = cleaned_data.get("is_current_edu", False)
                if commit:
                    education.save()

        return fpl_member


class PersonForm(forms.ModelForm):

    # --- Basic Information
    first_name = forms.CharField(label="First Name")
    last_name = forms.CharField(label="Last Name")
    gender = forms.ChoiceField(
        label="Gender", choices=Person.GENDER_CHOICES, required=False, initial="N"
    )
    bio = forms.CharField(
        label="Biography", widget=forms.Textarea(attrs={"rows": 3}), required=False
    )
    photo = forms.ImageField(label="Photo", required=False)
    role = forms.ModelChoiceField(
        label="Organization - Role",
        queryset=Role.objects.all(),
        empty_label="--- Select Organization / Role ---",
    )

    # --- Contact Information
    email = forms.EmailField(label="Email Address", required=False)
    phone_country_code = forms.CharField(
        label="Country Code",
        initial="977",
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "977"}),
    )
    phone_number = forms.CharField(label="Phone Number", required=False)
    address = forms.CharField(
        label="Address", widget=forms.Textarea(attrs={"rows": 2}), required=False
    )
    emergency_contact_name = forms.CharField(
        label="Emergency Contact Name", required=False
    )
    emergency_contact_phone = forms.CharField(
        label="Emergency Contact Phone", required=False
    )
    emergency_contact_relationship = forms.CharField(
        label="Relationship to Emergency Contact", required=False
    )

    class Meta:
        model = Person
        fields = ["first_name", "last_name", "role", "bio", "gender", "photo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        roles = []
        for role in Role.objects.select_related("organization").all():
            label = f"{role.organization.name} - {role.name}"
            roles.append((role.pk, label))
        self.fields["role"].choices = [("", "--- Select Role ---")] + roles

        if self.instance and self.instance.pk:
            person = self.instance

            if person.role:
                self.fields["organization"].initial = person.role.organization

            # Populate Contact fields if contact exists
            if hasattr(person, "contact") and person.contact:
                contact = person.contact
                self.fields["email"].initial = contact.email
                self.fields["phone_country_code"].initial = contact.phone_country_code
                self.fields["phone_number"].initial = contact.phone_number
                self.fields["address"].initial = contact.address
                self.fields["emergency_contact_name"].initial = (
                    contact.emergency_contact_name
                )
                self.fields["emergency_contact_phone"].initial = (
                    contact.emergency_contact_phone
                )
                self.fields["emergency_contact_relationship"].initial = (
                    contact.emergency_contact_relationship
                )

    def clean(self):
        cleaned_data = super().clean()

        # Validate that first_name and last_name are provided
        first_name = cleaned_data.get("first_name", "").strip()
        last_name = cleaned_data.get("last_name", "").strip()

        if not first_name:
            raise forms.ValidationError("First name is required.")
        if not last_name:
            raise forms.ValidationError("Last name is required.")

        return cleaned_data

    def save(self, commit=True):
        person = super().save(commit=False)
        cleaned_data = self.cleaned_data

        if commit:
            person.save()

        # Handle PersonContact creation/update only if contact info is provided
        contact_fields = [
            "email",
            "phone_number",
            "address",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relationship",
        ]

        has_contact_info = any(
            cleaned_data.get(field, "").strip() for field in contact_fields
        )

        if has_contact_info:
            if hasattr(person, "contact") and person.contact:
                # Update existing contact
                contact = person.contact
            else:
                # Create new contact
                contact = PersonContact()

            contact.email = cleaned_data.get("email", "")
            contact.phone_country_code = cleaned_data.get("phone_country_code", "977")
            contact.phone_number = cleaned_data.get("phone_number", "")
            contact.address = cleaned_data.get("address", "")
            contact.emergency_contact_name = cleaned_data.get(
                "emergency_contact_name", ""
            )
            contact.emergency_contact_phone = cleaned_data.get(
                "emergency_contact_phone", ""
            )
            contact.emergency_contact_relationship = cleaned_data.get(
                "emergency_contact_relationship", ""
            )

            if commit:
                contact.save()
                if not hasattr(person, "contact") or not person.contact:
                    person.contact = contact
                    person.save()

        return person
