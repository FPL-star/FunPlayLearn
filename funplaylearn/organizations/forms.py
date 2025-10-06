from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from core.models import Palika, OrganizationContact, OrganizationType, SchoolType, Class
from organizations.models import Organization, Role, School, Schoolclass


class OrganizationForm(forms.ModelForm):
	class Meta:
		model=Organization
		fields=[
			"name",
			"palika",
			"contact",
			"org_type",
			"latitude",
			"longitude",
			"general_location",
			"active"
		
		]
	#--Contact Info
	email = forms.EmailField(label="Email Address")
	phone_country_code = forms.CharField(
		label="Country Code", initial="977", max_length=5, required=False
	)
	phone_number = forms.CharField(label="Phone Number", required=False)
	address = forms.CharField(
		label="Address", widget=forms.Textarea(attrs={"rows": 2}), required=False
	)
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		#this is for editing existing orgs
		if self.instance and self.instance.pk:
			contact=getattr(self.instance, "contact", None)
			if contact:
				self.fields["email"].initial = contact.email
				self.fields["phone_country_code"].initial = contact.phone_country_code
				self.fields["phone_number"].initial = contact.phone_number
				self.fields["address"].initial = contact.address
		
		#we shouldnot need a clean method because the fields are either from orgs or contact models
		
	def save(self, commit=True):
		Organization=super().save(commit=False)
		cleaned_data=self.cleaned_data
		contact_fields={
			"email":cleaned_data.get("email"),
			"phone_country_code":cleaned_data.get("phone_country_code"),
			"phone_number":cleaned_data.get("phone_number"),
			"address":cleaned_data.get("address"),
		}
		if any(cleaned_data.get(f) for f in contact_fields):
			if hasattr(Organization, "contact"):#we are saying if its an existing org with contact we just load that or else we create a new one
				contact=Organization.contact
			else:
				contact=OrganizationContact()
				contact.email=cleaned_data.get("email")
				contact.phone_country_code=cleaned_data.get("phone_country_code")
				contact.phone_number=cleaned_data.get("phone_number")
				contact.address=cleaned_data.get("address")
				contact.is_organization=True
				contact.save()
				Organization.contact=contact
		if commit:
			Organization.save()
		return Organization
		


class SchoolForm(forms.ModelForm):
	class Meta:
		model=School
		fields=[
			"organization",
			"school_type",
			"class_1_fee",
			"provides_food",	
			"first_session_date",
			"start_time_firsthalf",
			"start_time_secondhalf",
			"session_duration",
		]
	#core info 
	school_name=forms.CharField(label="school_name", required=False)
	school_palika=forms.ModelChoiceField(label="Palika", queryset=Palika.objects.all(), required=True)
	#contact info 
	email = forms.EmailField(label="email_address")
	phone_country_code = forms.CharField(
		label="country_code", initial="977", max_length=5, required=False
	)
	phone_number = forms.CharField(label="phone_number", required=False)
	address = forms.CharField(
		label="address", widget=forms.Textarea(attrs={"rows": 2}), required=False
	)

	#gps info
	latitude=forms.DecimalField(label="latitude", max_digits=9, decimal_places=6, required=True)
	longitude=forms.DecimalField(label="longitude", max_digits=9, decimal_places=6, required=True)
	general_location=forms.CharField(label="general_location", max_length=255	, required=True)

	#active status
	active=forms.BooleanField(label="active", required=False)
	
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
	
		if not (self.instance and self.instance.pk):
			return #this is saying if if there is no data that matches in the db just return,so initialize the from with no data
		 
		organization= getattr(self.instance, "organization", None) #this is getting the org attribite from the school model instanceand defaultingto none if not found
		if organization: #checking if its none
			self.fields["school_name"].initial=organization.name #pre populating the form fields with existing data with ".initial"
			self.fields["school_palika"].initial=organization.palika
			self.fields["latitude"].initial=organization.latitude
			self.fields["longitude"].initial=organization.longitude
			self.fields["general_location"].initial=organization.general_location
			self.fields["active"].initial=organization.active	

			contact=getattr(organization, "contact", None)
			if contact:
				self.fields["email"].initial = contact.email
				self.fields["phone_country_code"].initial = contact.phone_country_code
				self.fields["phone_number"].initial = contact.phone_number
				self.fields["address"].initial = contact.address
	
	def save(self, commit=True):
		#add condition for when it doesnot exits(i.e create mode )
		if self.instance and hasattr(self.instance, "organization"):
			organization=self.instance.organization
			
			organization.name=self.cleaned_data.get("school_name")#this just checks if any of the prepopulated stuff has changed(i.e editing)
			organization.palika=self.cleaned_data.get("school_palika")
			organization.latitude=self.cleaned_data.get("latitude")
			organization.longitude=self.cleaned_data.get("longitude")
			organization.general_location=self.cleaned_data.get("general_location")
			organization.active=self.cleaned_data.get("active")
			organization.org_type=OrganizationType.objects.get(name="School")#we are setting the org type to school since its a school form
			organization.save()
			
			contact=getattr(organization,"contact", None)
			if contact:
				contact.email=self.cleaned_data.get("email")
				contact.phone_country_code=self.cleaned_data.get("phone_country_code")
				contact.phone_number=self.cleaned_data.get("phone_number")
				contact.address=self.cleaned_data.get("address")
				contact.save()
		else:
			contact=OrganizationContact.objects.create(
				email=self.cleaned_data.get("email"),
				phone_country_code=self.cleaned_data.get("phone_country_code"),
				phone_number=self.cleaned_data.get("phone_number"),
				address=self.cleaned_data.get("address"),
				is_organization=True,
			)
			organization=Organization.objects.create(
				name=self.cleaned_data.get("school_name"),
				palika=self.cleaned_data.get("school_palika"),
				contact=contact,
				latitude=self.cleaned_data.get("latitude"),
				longitude=self.cleaned_data.get("longitude"),
				general_location=self.cleaned_data.get("general_location"),
				active=self.cleaned_data.get("active"),
				org_type=OrganizationType.objects.get(name="School"),
	)
		school=super().save(commit=False)#saved without org info in memory not db , to avoid error,we are creating the instace and then adding to it
		school.organization=organization#now we save the org info
		school.save()
		return school

