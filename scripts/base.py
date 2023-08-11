import sys, os, django


def django_env():
    BASE_DIR = os.path.dirname(os.path.dirname("scripts"))
    sys.path.append(BASE_DIR)
    os.environ["DJANGO_SETTINGS_MODULE"] = "phurti.settings"
    django.setup()
