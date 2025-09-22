# forms.py
from django import forms
from django.contrib.auth.models import User
from core.models import PersonContact
from people.models import FPLMember, Person, PersonEducation, PersonSensitiveData
from organizations.models import Role


class FPLMemberForm(forms.ModelForm):

    # --- Django User Creation
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    # --- Person Fields
    first_name = forms.CharField(label="First Name")
    last_name = forms.CharField(label="Last Name")
    email = forms.EmailField()
    bio = forms.CharField()
    photo = forms.ImageField()

    # --- FPLMember fields
    role = forms.ModelChoiceField(
        queryset=Role.objects.filter(organization__name="FunPlayLearn")
    )

    # --- Contact Fields
    email = forms.EmailField(label="Email")
    phone_country_code = forms.CharField(
        label="Country Code", initial="977", required=False
    )
    phone_number = forms.CharField(label="Phone Number")
    address = forms.CharField(label="Address")
    emergency_contact_name = forms.CharField(label="Emergency contact name")
    emergency_contact_phone = forms.CharField(label="Emergency contact phone")
    emergency_contact_relationship = forms.CharField(
        label="Emergency contact relationship"
    )

    # --- Education Fields
    edu_level = forms.ChoiceField(
        label="Highest education level", choices=PersonEducation.EDUCATION_LEVEL_CHOICES
    )
    edu_institution = forms.CharField(label="Educational Instution Name")
    field_of_study = forms.CharField(label="Field of Study")
    is_current_edu = forms.BooleanField(label="Currently enrolled?", required=False)

    # --- Sensitive Data Fields
    date_of_birth = forms.DateField(label="Date Of Birth")
    gender = forms.ChoiceField(label="Gender", choices=Person.GENDER_CHOICES)
    blood_type = forms.ChoiceField(
        label="Blood Type", choices=PersonSensitiveData.BLOOD_TYPE_CHOICES
    )
    bank_account = forms.CharField(label="Bank account number", required=False)
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            fpl_member = self.instance

            person = fpl_member.person
            user = fpl_member.user

            self.fields["first_name"].initial = person.first_name
            self.fields["last_name"].initial = person.last_name
            self.fields["username"].initial = user.username

            if hasattr(person, "contact"):
                self.fields["email"].initial = person.contact.email
                self.fields["phone_country_code"] = person.contact.phone_country_code
                self.fields["phone_number"] = person.contact.phone_number

            if hasattr(fpl_member, "personsensitivedata"):
                sd = fpl_member.personsensitivedata
                self.fields["bank_account"].initial = sd.bank_account
                self.fields["pan_number"].initial = sd.pan_number

    def save(self, commit=True):
        fpl_member = super().save(commit=False)
        cleaned_data = self.cleaned_data

        if fpl_member.pk:
            user = fpl_member.user
            user.username = cleaned_data["username"]
            if cleaned_data["password"]:
                user.set_password(cleaned_data["password"])
            user.save()
        else:
            user = User.objects.create_user(
                username=cleaned_data["username"], password=cleaned_data["password"]
            )
            fpl_member.user = user

        if fpl_member.pk:
            person = fpl_member.person
            person.first_name = cleaned_data["first_name"]
            person.save()

            contact, created = PersonContact.objects.get_or_create(person=person)
            contact.email = cleaned_data["email"]
            contact.save()
        else:
            contact = PersonContact.objects.create(email=cleaned_data["email"])
            person = Person.objects.create(
                first_name=cleaned_data["first_name"],
                last_name=cleaned_data["last_name"],
                contact=contact,
                role=cleaned_data["role"],
            )
            fpl_member.person = person

        if commit:
            fpl_member.save()

        return fpl_member
