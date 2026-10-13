# Nepali Coffee ☕🇳🇵

**Coffee is not fashion, it's our tradition.**

Nepali Coffee is a Django-based web project designed to help people
discover Nepal's coffee producers, learn about coffee, and explore local
coffee products. It includes a searchable producer directory,
educational content, account-based buyer and seller workflows, reviews,
and an administration area.

> **Project status:** Development project. The repository configuration
> currently includes development settings (including `DEBUG = True`, a
> development-only secret key, SQLite, and console email). Do not deploy
> publicly until the production configuration and deployment checklist
> below have been completed and tested.

## Table of contents

- [Features](#features)
- [Technology stack](#technology-stack)
- [User roles](#user-roles)
- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Run locally](#run-locally)
- [Database and migrations](#database-and-migrations)
- [Useful commands](#useful-commands)
- [Security and production
  deployment](#security-and-production-deployment)
- [Data and moderation notes](#data-and-moderation-notes)
- [Limitations](#limitations)
- [Contributing](#contributing)
- [License](#license)

## Features

- Responsive homepage and navigation.
- Producer directory with keyword search and filters such as location,
  province/district, coffee type, processing method, price range,
  rating, and other available listing attributes.
- Producer detail pages with profile information, product listings,
  contact details, and optional OpenStreetMap links when coordinates
  are provided.
- Coffee guide, coffee history, recipes, About Us, and Contact pages.
- Buyer and seller registration, login, and role-aware dashboards.
- Buyers can save producers and submit or edit a review for a
  producer.
- Sellers can request ownership of an existing producer listing.
- Seller listing and product management is available only after an
  administrator approves the relevant claim.
- Django administration at `/admin/`.
- Contact messages are stored in the database.
- SQLite is configured by default for local development.

## Technology stack

- **Backend:** Python and Django
- **Frontend:** HTML, CSS, JavaScript, Bootstrap-based responsive
  styling
- **Database:** SQLite by default
- **Image handling:** Pillow
- **Timezone:** Asia/Kathmandu

## User roles

### Buyer

- Browse and filter producer listings.
- View producer and coffee information.
- Save favourite producers.
- Submit and edit a review for a producer.

### Seller

- Register with the Seller role.
- Request ownership of a producer listing.
- After administrator approval, manage the linked producer profile and
  that producer's products.
- Seller access does not grant permission to manage another seller's
  listing.

### Administrator

- Created through Django's `createsuperuser` command or by an
  authorized administrator.
- Uses Django admin at `/admin/`.
- Public registration does not provide an Administrator role.
  Administrative access depends on Django's staff/superuser
  permissions.

## Project structure

```text
nepal_coffee_marketplace/
├── manage.py
├── requirements.txt
├── README.md
├── coffee_market/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── directory/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   └── management/
├── templates/
│   ├── base.html
│   └── directory/
└── static/
    ├── css/
    └── js/
```

The exact files may change as the project develops. Local database
files, virtual environments, secrets, and generated files should not be
committed to GitHub.

## Requirements

- Python 3.11 or newer (use a Python version supported by the
  installed Django release).
- pip
- Git (recommended)
- A terminal such as PowerShell, Command Prompt, or a Unix shell.

## Run locally

### 1. Clone the repository
```bash
git clone https://github.com/manojbudhathoki/Nepal-Coffee-Market.git
cd nepal_coffee_marketplace
```

### 2. Create and activate a virtual environment

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

**macOS/Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure a local development secret

The current starter settings use a development-only key. For safer local
configuration, update `coffee_market/settings.py` to read `SECRET_KEY`
and `DEBUG` from environment variables before using the example below.

**Windows PowerShell**

```powershell
$env:DJANGO_DEBUG = "True"
$env:DJANGO_SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
$env:DJANGO_ALLOWED_HOSTS = "127.0.0.1,localhost"
```

These values are for local development and the current terminal session
only. Generate a separate secret for production. Do not commit secret
keys to GitHub.

### 5. Apply database migrations

If migration files are already included in the repository:

```bash
python manage.py migrate
```

If this is a development checkout and the app's initial migrations have
not yet been created, generate and review them first:

```bash
python manage.py makemigrations directory
python manage.py migrate
```

Commit reviewed migration files to the repository. Do not depend on
generating schema migrations for the first time on a production server.

### 6. Create an administrator

```bash
python manage.py createsuperuser
```

Follow the prompts. Do not make normal buyer or seller accounts
staff/superusers.

### 7. Run the development server

```bash
python manage.py check
python manage.py runserver
```

Open:

- Website: http://127.0.0.1:8000/
- Django admin: http://127.0.0.1:8000/admin/

The Django development server is for local development only, not public
production hosting.

## Database and migrations

SQLite is the default database for local development. Django stores data
in the configured SQLite database file.

- Back up the database before schema changes.
- Keep migration files under version control.
- Apply migrations with `python manage.py migrate`.
- For a public deployment, verify that the host provides persistent
  storage if SQLite is retained.
- Consider a managed production database such as PostgreSQL when
  traffic, concurrent writes, operational needs, or hosting
  constraints justify it.
- Test database backups and restoration rather than assuming a backup
  is usable.

## Useful commands

```bash
# Check project configuration
python manage.py check

# Run automated tests
python manage.py test

# Check whether model changes need migrations
python manage.py makemigrations --check --dry-run

# Preview pending migrations
python manage.py migrate --plan

# Apply migrations
python manage.py migrate

# Collect static files after STATIC_ROOT is configured
python manage.py collectstatic

# Run Django's deployment checks using production settings
python manage.py check --deploy
```

A successful command does not replace manual and browser testing. If
`python manage.py test` reports zero tests, add tests for the core
application workflows.

## Security and production deployment

**Do not deploy the current development settings unchanged.** Before
making the website publicly accessible:

1.  Set `DEBUG = False` in production.
2.  Load a unique, randomly generated `SECRET_KEY` from the hosting
    environment; never commit it to the repository.
3.  Configure `ALLOWED_HOSTS` for the real domain.
4.  Configure `CSRF_TRUSTED_ORIGINS` with the exact HTTPS origins
    required by the site.
5.  Serve the site over HTTPS and configure secure session and CSRF
    cookies.
6.  Enable HTTP-to-HTTPS redirection only after the hosting proxy/server
    is correctly configured.
7.  Configure HSTS only after HTTPS is working across the entire site;
    start cautiously and understand subdomain implications before
    enabling them.
8.  Configure `STATIC_ROOT`, run `collectstatic`, and serve static files
    using the hosting provider's recommended setup.
9.  Use a production WSGI server and follow the host's Django deployment
    instructions. Do not use `runserver` as the public server.
10. Configure a real email backend if email delivery is needed. The
    current project uses Django's console email backend for development.
11. Add backups, monitoring, logging, dependency updates, spam/rate
    limiting, and an incident recovery plan.
12. Run `python manage.py check --deploy` with the actual production
    settings and test the deployed site.

Environment-variable names and the production setup depend on the
hosting platform. Keep local and production configuration separate.
Never paste real credentials into this README or GitHub.

## Data and moderation notes

- Verify all producer names, locations, contact details, product
  details, prices, stock, certifications, and export claims before
  publishing them.
- Do not present fictional or demonstration records as real
  businesses.
- Administrator-supplied producer ratings are separate from
  customer-review averages.
- Customer reviews are account-based and are not proof of a verified
  purchase.
- Producer claims require administrator approval; a submitted claim
  alone does not verify a business.
- Contact form submissions are stored in the database. Set an
  appropriate retention policy and add spam protection before public
  launch.
- Review moderation and publication settings should match the policy
  you intend to operate.

## Limitations

- The project is a developing directory/marketplace, not a complete
  online payment platform.
- No payment gateway is configured.
- No external map API key is required for optional OpenStreetMap
  links.
- Email delivery is not configured for production by default.
- A production deployment and full browser/security test must be
  completed before the site is described as production-ready.
- The user interface is primarily English-language; full Nepali
  localization is not included by default.

## Contributing

Contributions and constructive suggestions are welcome.

1.  Fork the repository.
2.  Create a branch for your change.
3.  Make a focused change and test it.
4.  Submit a pull request describing the change and any testing
    performed.

Do not include real user data, production database files, secret keys,
passwords, or other credentials in commits.
---

**Project:** Nepali Coffee\
**Tagline:** _Coffee is not fashion, it's our tradition._\
**Author:** Manoj Budhathoki
