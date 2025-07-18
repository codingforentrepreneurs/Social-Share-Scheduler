import os
import pathlib
import sys

NOTEBOOKS_DIR = pathlib.Path(__file__).parent
REPO_DIR = NOTEBOOKS_DIR.parent
DJANGO_PROJECT_ROOT = REPO_DIR / "src"
DJANGO_SETTINGS_MODULE = "cfehome.settings"


def init(verbose=False):
    os.chdir(DJANGO_PROJECT_ROOT)
    sys.path.insert(0, str(DJANGO_PROJECT_ROOT))
    if verbose:
        print(f"Changed working directory to: {DJANGO_PROJECT_ROOT}")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS_MODULE)
    os.environ.setdefault("INNGEST_DEV", "1")
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    # os.environ.setdefault(
    #     "DATABASE_URL",
    #     "postgres://postgres:postgres@localhost:5432/postgres",
    # )
    import django

    django.setup()