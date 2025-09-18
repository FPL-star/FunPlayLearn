## Working Project Structure

This is the _suggested_ project structure for now, although we can (and should!) modify it as required during development. It is a suggestion, not an order.

```bash
FunPlayLearn/
├─ core/                           # Django app - shared utilities
│   ├─ __init__.py
│   ├─ apps.py
│   ├─ models.py                   # Abstract base classes, mixins, Grade, Weekday, Palika 
│   ├─ admin.py                    # Site-wide admin customizations, reference data
│   ├─ utils.py
│   ├─ mixins.py
│   └─ migrations/
├─ organizations/                  # Django app
│   ├─ __init__.py
│   ├─ apps.py  
│   ├─ models.py                   # Organization, School, SchoolDay, SchoolGrade
│   ├─ admin.py                    # Admin for org models
│   ├─ services.py                 # Business logic
│   ├─ migrations/
│   └─ tests.py
├─ people/                         # Django app
│   ├─ __init__.py
│   ├─ apps.py
│   ├─ models.py                   # Person, Contact, PersonSensitiveData, Role
│   ├─ admin.py                    # Person management admin
│   ├─ services.py
│   ├─ migrations/
│   └─ tests.py
├─ sessions/                       # Django app
│   ├─ __init__.py
│   ├─ apps.py
│   ├─ models.py                   # Session, SessionPhoto
│   ├─ admin.py                    # Session admin
│   ├─ migrations/
│   └─ tests.py
├─ games/                          # Django app
│   ├─ __init__.py
│   ├─ apps.py
│   ├─ models.py                   # Game
│   ├─ admin.py                    # Game admin
│   ├─ migrations/
│   └─ tests.py
├─ fpl/                           # Django app
│   ├─ __init__.py
│   ├─ apps.py
│   ├─ models.py                   # FPLMember
│   ├─ admin.py                    # FPL program admin
│   ├─ migrations/
│   └─ tests.py
├─ mediafiles/                     # Django app
│   ├─ __init__.py
│   ├─ apps.py
│   ├─ models.py                   # File/image models
│   ├─ admin.py                    # Media admin
│   ├─ image_processors.py
│   ├─ storage_backends.py
│   ├─ migrations/
│   └─ tests.py
├─ frontend/                       # Django app - public views
│   ├─ __init__.py
│   ├─ apps.py
│   ├─ views.py                    # Public pages
│   ├─ urls.py                     # Public URL patterns
│   ├─ templates/
│   │   ├─ base.html
│   │   ├─ index.html
│   │   ├─ about.html
│   │   ├─ people/
│   │   └─ program/
│   ├─ static/
│   │   ├─ css/
│   │   ├─ js/
│   │   └─ images/
│   ├─ templatetags/               # Custom template tags
│   └─ context_processors.py       # Context processors
├─ data_entry/                     # Django app - internal forms
│   ├─ __init__.py
│   ├─ apps.py
│   ├─ views.py                    # Form views
│   ├─ forms.py                    # Django forms
│   ├─ urls.py                     # Internal URL patterns
│   ├─ templates/
│   │   ├─ data_entry/
│   │   └─ forms/
│   └─ permissions.py              # Custom permissions
├─ api/                           # Django app - API views
│   ├─ __init__.py
│   ├─ apps.py
│   ├─ v1/
│   │   ├─ serializers.py
│   │   ├─ views.py
│   │   └─ urls.py
│   ├─ permissions.py
│   └─ authentication.py
├─ accounts/                       # Django app - authentication
│   ├─ __init__.py
│   ├─ apps.py
│   ├─ models.py                   # Custom user model (if needed)
│   ├─ admin.py                    # User admin customizations
│   ├─ views.py                    # Login/logout/profile views
│   ├─ forms.py                    # Auth forms
│   ├─ urls.py
│   ├─ templates/registration/
│   ├─ migrations/
│   └─ tests.py
└─ FunPlayLearn/                      # Main project directory
    ├─ __init__.py
    ├─ settings.py
    ├─ urls.py                     # Root URL config
    ├─ wsgi.py
    └─ asgi.py   
```
