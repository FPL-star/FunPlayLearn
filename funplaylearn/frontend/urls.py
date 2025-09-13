from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("about_us", TemplateView.as_view(template_name="about_us.html"), name="about_us"),
    path("resources", TemplateView.as_view(template_name="resources.html"), name="resources"),
	 path("join_us", TemplateView.as_view(template_name="join_us.html"), name="join_us"),
]