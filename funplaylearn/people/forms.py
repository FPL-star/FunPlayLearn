
from django import forms
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from people.models import (
    FPLMember,
    Person,
    PersonEducation,
    PersonSensitiveData,
    PersonContact,
)
from organizations.models import Role


class FPLMemberForm(forms.ModelForm):
    # --- Basic Information
    first_name = forms.CharField(label="First Name")
    last_name = forms.CharField(label="Last Name")
    photo = forms.ImageField(label="Photo", required=False)
    bio = forms.CharField(
        label="Biography", widget=forms.Textarea(attrs={"rows": 3}), required=False
    )

    # --- Organization Information
    role = forms.ModelChoiceField(
        label="Role", queryset=Role.objects.filter(organization__name="FunPlayLearn")
    )

    # --- Contact Information
    email = forms.EmailField(label="Email Address")
    phone_country_code = forms.CharField(
        label="Country Code", initial="977", max_length=5, required=False
    )
    phone_number = forms.CharField(label="Phone Number", required=False)
    address = forms.CharField(
        label="Address", widget=forms.Textarea(attrs={"rows": 2}), required=False
    )

    # --- Emergency Contact
    emergency_contact_name = forms.CharField(
        label="Emergency Contact Name", required=False
    )
    emergency_contact_phone = forms.CharField(
        label="Emergency Contact Phone", required=False
    )
    emergency_contact_relationship = forms.CharField(
        label="Relationship to Emergency Contact", required=False
    )

    # --- Education
    edu_level = forms.ChoiceField(
        label="Highest Education Level",
        choices=[("", "--- Select Education Level ---")]
        + PersonEducation.EDUCATION_LEVEL_CHOICES,
        required=False,
    )
    edu_institution = forms.CharField(label="Educational Institution", required=False)
    edu_field_of_study = forms.CharField(label="Field of Study", required=False)
    is_current_edu = forms.BooleanField(label="Currently Enrolled", required=False)

    # --- Medical & Financial
    blood_type = forms.ChoiceField(
        label="Blood Type",
        choices=[("", "--- Select Blood Type ---")]
        + PersonSensitiveData.BLOOD_TYPE_CHOICES,
        required=True,
    )
    gender = forms.ChoiceField(label="Gender", choices=Person.GENDER_CHOICES)
    date_of_birth = forms.DateField(
        label="Date Of Birth",
        widget=forms.DateInput(attrs={"type": "date"}),
        required=True,
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

        if not (self.instance and self.instance.pk):
            return

        person = getattr(self.instance, "person", None)
        if person:
            # Basic info
            self.fields["first_name"].initial = person.first_name
            self.fields["last_name"].initial = person.last_name
            self.fields["gender"].initial = person.gender
            self.fields["bio"].initial = person.bio
            self.fields["photo"].initial = person.photo
            self.fields["role"].initial = person.role

            # Contact info
            contact = getattr(person, "contact", None)
            if contact:
                for field_name in [
                    "email",
                    "phone_country_code",
                    "phone_number",
                    "address",
                    "emergency_contact_name",
                    "emergency_contact_phone",
                    "emergency_contact_relationship",
                ]:
                    self.fields[field_name].initial = getattr(contact, field_name, "")

        # Sensitive data
        sd = getattr(self.instance, "personsensitivedata", None)
        if sd:
            self.fields["blood_type"].initial = sd.blood_type
            self.fields["date_of_birth"].initial = sd.date_of_birth
            self.fields["bank_account"].initial = sd.bank_account
            self.fields["pan_number"].initial = sd.pan_number

        # Education
        edu = getattr(self.instance, "personeducation", None)
        if edu:
            self.fields["edu_level"].initial = edu.level
            self.fields["edu_institution"].initial = edu.institution
            self.fields["edu_field_of_study"].initial = edu.field_of_study
            self.fields["is_current_edu"].initial = edu.is_current

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get("first_name", "").strip()
        last_name = cleaned_data.get("last_name", "").strip()

        if not first_name:
            raise forms.ValidationError("First name is required.")
        if not last_name:
            raise forms.ValidationError("Last name is required.")

        # Check username for new instances
        if not (self.instance and self.instance.pk):
            username = f"{first_name.lower()}.{last_name.lower()}@funplaylearn.org"
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError(
                    f"A user with the name '{first_name} {last_name}' already exists."
                )
        return cleaned_data

    def save(self, commit=True):
        if self.instance and self.instance.pk:
            user = self.instance.user
            user.first_name = self.cleaned_data["first_name"]
            user.last_name = self.cleaned_data["last_name"]
            user.email = self.cleaned_data.get("email", "")
            user.save()
        else:
            username = f"{self.cleaned_data['first_name'].lower()}.{self.cleaned_data['last_name'].lower()}@funplaylearn.org"
            password = get_random_string(length=12)
            user = User.objects.create_user(
                username=username,
                password=password,
                email=self.cleaned_data.get("email", ""),
                first_name=self.cleaned_data["first_name"],
                last_name=self.cleaned_data["last_name"],
            )

        if self.instance and hasattr(self.instance, "person"):
            person = self.instance.person
            contact = getattr(person, "contact", None)
            person.first_name = self.cleaned_data["first_name"]
            person.last_name = self.cleaned_data["last_name"]
            person.role = self.cleaned_data["role"]
            person.gender = self.cleaned_data["gender"]
            person.bio = self.cleaned_data.get("bio", "")
            if self.cleaned_data.get("photo"):
                person.photo = self.cleaned_data.get("photo")
            person.save()
            if contact:
                contact.email = self.cleaned_data.get("email", "")
                contact.phone_country_code = self.cleaned_data.get(
                    "phone_country_code", "977"
                )
                contact.phone_number = self.cleaned_data.get("phone_number", "")
                contact.address = self.cleaned_data.get("address", "")
                contact.emergency_contact_name = self.cleaned_data.get(
                    "emergency_contact_name", ""
                )
                contact.emergency_contact_phone = self.cleaned_data.get(
                    "emergency_contact_phone", ""
                )
                contact.emergency_contact_relationship = self.cleaned_data.get(
                    "emergency_contact_relationship", ""
                )
                contact.save()
        else:
            contact = PersonContact.objects.create(
                email=self.cleaned_data.get("email", ""),
                phone_country_code=self.cleaned_data.get("phone_country_code", "977"),
                phone_number=self.cleaned_data.get("phone_number", ""),
                address=self.cleaned_data.get("address", ""),
                emergency_contact_name=self.cleaned_data.get(
                    "emergency_contact_name", ""
                ),
                emergency_contact_phone=self.cleaned_data.get(
                    "emergency_contact_phone", ""
                ),
                emergency_contact_relationship=self.cleaned_data.get(
                    "emergency_contact_relationship", ""
                ),
            )
            person = Person.objects.create(
                first_name=self.cleaned_data["first_name"],
                last_name=self.cleaned_data["last_name"],
                role=self.cleaned_data["role"],
                gender=self.cleaned_data["gender"],
                bio=self.cleaned_data.get("bio", ""),
                photo=self.cleaned_data.get("photo"),
                contact=contact,
            )

        fpl_member = super().save(commit=False)
        fpl_member.user = user
        fpl_member.person = person
        fpl_member.save()
        sd_defaults = {
            "date_of_birth": self.cleaned_data.get("date_of_birth"),
            "blood_type": self.cleaned_data.get("blood_type", ""),
            "bank_account": self.cleaned_data.get("bank_account"),
            "pan_number": self.cleaned_data.get("pan_number"),
        }

        sd, created = PersonSensitiveData.objects.get_or_create(
            fpl_member=fpl_member, defaults=sd_defaults
        )
        if not created:

            for key, value in sd_defaults.items():
                setattr(sd, key, value)
            sd.save()

        edu_defaults = {
            "level": self.cleaned_data.get("edu_level"),
            "institution": self.cleaned_data.get("edu_institution", ""),
            "field_of_study": self.cleaned_data.get("edu_field_of_study", ""),
            "is_current": self.cleaned_data.get("is_current_edu", False),
        }

        edu, created = PersonEducation.objects.get_or_create(
            fpl_member=fpl_member, defaults=edu_defaults
        )
        if not created:
            for key, value in edu_defaults.items():
                setattr(edu, key, value)
            edu.save()

        return fpl_member


class PersonForm(forms.ModelForm):
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
        label="Country Code", initial="977", max_length=5, required=False
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
        if self.instance and self.instance.pk:
            contact = getattr(self.instance, "contact", None)
            if contact:
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

    def save(self, commit=True):
        person = super().save(commit=False)
        cleaned_data = self.cleaned_data
        contact_fields = [
            "email",
            "phone_number",
            "address",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relationship",
        ]
        if any(cleaned_data.get(f) for f in contact_fields):
            if hasattr(person, "contact") and person.contact:
                contact = person.contact
            else:
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
            contact.save()
            person.contact = contact

        if commit:
            person.save()
        return person
