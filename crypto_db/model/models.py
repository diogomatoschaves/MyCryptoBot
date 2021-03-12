import sys

try:
    from django.db import models
except Exception:
    print("Exception: Django Not Found, please install it with \"pip install django\".")
    sys.exit()


class Asset(models.Model):

    symbol = models.TextField(primary_key=True)
    name = models.TextField(null=True)

