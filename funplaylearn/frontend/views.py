from django.shortcuts import render

# Home page view
def simple_page(request, page):
    template_name = f"{page}.html"
    return render(request, template_name)