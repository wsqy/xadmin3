# AGENTS.md — xadmin

## What this is

xadmin v0.6.x — a drop-in replacement for Django admin with Bootstrap UI, plugins, and dashboard support. Targets **Django >= 1.9**, **Python 2.7 / 3.4**.

## Directory layout

| Path | Purpose |
|---|---|
| `xadmin/` | Library package (the actual product) |
| `xadmin/views/` | Class-based admin views (List, Create, Update, Delete, Detail, Dashboard, etc.) |
| `xadmin/plugins/` | Extensible plugin system (30+ built-in plugins) |
| `xadmin/templatetags/` | Custom template tags |
| `xadmin/templates/` | HTML templates (Bootstrap 3) |
| `xadmin/migrations/` | DB migrations for xadmin's own models (Log, UserSettings) |
| `demo_app/` | Demo Django project for local testing |
| `tests/` | Test harness (NOT standard Django `manage.py test`) |

## Commands

**Run tests** (from repo root):
```bash
cd tests/ && python runtests.py
```
Run a specific test module:
```bash
cd tests/ && python runtests.py view_base site
```

**Run demo app**:
```bash
cd demo_app
./manage.py migrate
./manage.py runserver
```
Default admin credentials: `admin` / `admin`

**Install for development**:
```bash
pip install -r requirements.txt
pip install -e .
```

## Architecture notes

### Registration uses `adminx.py`, NOT `admin.py`
- `xadmin.autodiscover()` scans each installed app for `adminx.py` (not `admin.py`).
- Admin classes are registered with `@xadmin.sites.register(Model)` decorator.
- The default site is `xadmin.sites.site` (analogous to `django.contrib.admin.site`).

### View system
- All views are class-based, inheriting from `BaseAdminView` or `ModelAdminView`.
- URL routing is pattern-based: `site.register_modelview(r'^$', ListAdminView, name='%s_%s_changelist')`.
- Views are composed via a plugin/mixin system — plugins can hook into any view method.

### Plugin system
- Plugins live in `xadmin/plugins/` and are listed in `xadmin/plugins/__init__.py` `PLUGINS` tuple.
- Each plugin module registers itself when imported.
- Exclude plugins at runtime via `XADMIN_EXCLUDE_PLUGINS` in Django settings.
- Plugin base class: `BaseAdminPlugin`.

### Crispy forms
- xadmin sets `CRISPY_TEMPLATE_PACK = 'bootstrap3'` automatically during `autodiscover()`.
- Uses `django-crispy-forms` for form rendering.

### Key dependencies
- `django-crispy-forms >= 1.6.0`
- `django-reversion >= 2.0.0` (optional, for object history)
- `django-formtools >= 1.0` (optional, for wizard forms)
- `django-import-export >= 0.5.1` (for data import/export)
- `xlwt` / `xlsxwriter` (optional, for Excel export)

## Testing quirks

- Tests use a **custom runner** (`tests/runtests.py`), not `manage.py test`.
- The runner dynamically adds test modules from `tests/xtests/` to `INSTALLED_APPS`.
- Test modules must be directories with `__init__.py`, `models.py`, `tests.py`, and optionally `adminx.py`.
- Base test class is `tests/xtests/base.py` (`BaseTest`), which provides `_create_superuser()` and `_mocked_request()`.
- Tests use SQLite in-memory database.
- The Travis CI config runs: `cd tests/ && python runtests.py base view_base`.

## Conventions

- Admin option classes are plain Python classes (not inheriting from anything), decorated with `@xadmin.sites.register(Model)`.
- List display customization: `list_display`, `list_display_links`, `list_filter`, `search_fields`, `list_editable`.
- Custom actions: define methods and assign to `actions` list.
- Dashboard widgets: register a class with `@xadmin.sites.register(views.website.IndexView)` and define `widgets` list.
- Global settings: register with `@xadmin.sites.register(views.BaseAdminView)` or `@xadmin.sites.register(views.CommAdminView)`.
- `allow_tags = True` on methods to render HTML in list display (Django < 2.0 convention).
