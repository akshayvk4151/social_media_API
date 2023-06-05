from django.contrib import admin

# Register your models here.

from django.apps import apps

app_name = 'social_media_api'

for model in apps.get_app_config(app_name).get_models():
    admin.site.register(model)