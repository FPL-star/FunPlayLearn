from django.db import models
from core.models import Palika, Contact
from core.utils import decrypt_field, encrypt_field

# TODO: Uncomment when Role model is ready
# from organization.models import Role


class Person(models.Model):
    """Table to track individual people"""

    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
        ("N", "Not specified"),
    ]

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "People"
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["first_name", "last_name"], name="idx_person_name"),
            models.Index(fields=["role"], name="idx_person_role"),
        ]

    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    # TODO: Uncomment when Role model is ready
    # role = models.ForeignKey(Role, on_delete=models.PROTECT, null=False, blank=False)
    role = models.CharField(
        max_length=100, default="Temporary Role"
    )  # TODO: Remove when Role model is ready
    contact = models.OneToOneField(
        Contact, on_delete=models.PROTECT, null=True, blank=True
    )
    bio = models.TextField(blank=True, null=False, default="")
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, default="N", blank=True, null=False
    )
    photo = models.ImageField(upload_to="people/", blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} [{self.role}]"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class FPLMember(models.Model):
    """Table to track people who are FPLMembers"""

    class Meta:
        indexes = [
            models.Index(fields=["person"], name="idx_fpl_person"),
            models.Index(fields=["palika"], name="idx_fpl_palika"),
            models.Index(fields=["palika", "active"], name="idx_palika_active"),
        ]

    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        related_name="fpl_member",
    )
    palika = models.ForeignKey(
        Palika, on_delete=models.PROTECT, related_name="fpl_members"
    )
    start_date = models.DateField()
    active = models.BooleanField(default=True)
    agreement = models.BooleanField(default=False)

    leave_date = models.DateField(null=True, blank=True)
    sim_returned = models.BooleanField(default=False)
    account_closed = models.BooleanField(default=False)
    certificate_issued = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.person.full_name} [Active: {self.active}]"


class PersonSensitiveData(models.Model):
    """Table to store an FPLMember's sensitive data with encryption"""

    BLOOD_TYPE_CHOICES = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    ]

    BLOOD_DONATION_COMPATIBILITY = {
        "O-": ["O-", "O+", "A+", "A-", "B+", "B-", "AB+", "AB-"],
        "O+": ["O+", "A+", "B+", "AB+"],
        "A-": ["A-", "A+", "AB-", "AB+"],
        "A+": ["A+", "AB+"],
        "B-": ["B-", "B+", "AB-", "AB+"],
        "B+": ["B+", "AB+"],
        "AB-": ["AB-", "AB+"],
        "AB+": ["AB+"],
    }

    # Blood donation compatibility reverse mapping
    BLOOD_RECEIVE_COMPATIBILITY = {}
    for donor, recipients in BLOOD_DONATION_COMPATIBILITY.items():
        for recipient in recipients:
            BLOOD_RECEIVE_COMPATIBILITY.setdefault(recipient, []).append(donor)

    class Meta:
        verbose_name = "Person Sensitive Data"
        ordering = ["blood_type", "fpl_member"]
        indexes = [models.Index(fields=["blood_type"], name="idx_blood_type")]

    fpl_member = models.OneToOneField(FPLMember, on_delete=models.PROTECT)
    date_of_birth = models.DateField()
    blood_type = models.CharField(
        max_length=3, choices=BLOOD_TYPE_CHOICES, blank=False, null=False
    )
    # Store sesnsitive fields as binary
    _bank_account = models.BinaryField(blank=True, null=True)
    _pan_number = models.BinaryField(blank=True, null=True)

    # --- Encrypted field properties ---
    @property
    def bank_account(self):
        return decrypt_field(self._bank_account)

    @bank_account.setter
    def bank_account(self, value):
        self._bank_account = encrypt_field(value)

    @property
    def pan_number(self):
        return decrypt_field(self._pan_number)

    @pan_number.setter
    def pan_number(self, value):
        self._pan_number = encrypt_field(value)

    @property
    def can_donate_to(self):
        """Return a list of blood types this person can donate to"""
        return self.BLOOD_DONATION_COMPATIBILITY.get(self.blood_type, [])

    @property
    def can_receive_from(self):
        """Return a list of blood types this person can receive from"""
        return self.BLOOD_RECEIVE_COMPATIBILITY.get(self.blood_type, [])

    def __str__(self):
        donate_to = ", ".join(self.can_donate_to) if self.can_donate_to else "None"
        receive_from = (
            ", ".join(self.can_receive_from) if self.can_receive_from else "None"
        )
        return (
            f"{self.fpl_member.person} [Sensitive Data]\n"
            f"Blood type: {self.blood_type or 'N/A'}\n"
            f"Donates to: [{donate_to}]\n"
            f"Receives from: [{receive_from}]"
        )


class PersonEducation(models.Model):
    """Table to track education of an FPLMember"""

    EDUCATION_LEVEL_CHOICES = [
        ("SCHOOL", "School (up to grade 10)"),
        ("PLUS_TWO", "Plus 2 / Higher Secondary"),
        ("BA", "Bachelor's"),
        ("MA", "Master's"),
        ("PHD", "Ph.D."),
        ("OTHER", "Other"),
    ]

    class Meta:
        verbose_name = "Person Education"
        ordering = ["fpl_member", "level", "is_current"]

    fpl_member = models.OneToOneField(
        FPLMember, on_delete=models.CASCADE, related_name="education"
    )
    level = models.CharField(
        "Highest education level",
        choices=EDUCATION_LEVEL_CHOICES,
        blank=False,
        null=False,
        max_length=20,
    )
    institution = models.CharField(
        "Institution of study", max_length=255, blank=True, null=False, default=""
    )
    field_of_study = models.CharField(
        "Field of study", max_length=255, blank=True, null=False, default=""
    )
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_level_display()} at {self.institution or '-'} [Currently studying: {self.is_current}]"
