from django.contrib import admin
from . import models


# Register your models here.
admin.site.register(models.SavedColor)
admin.site.register(models.CurrentColorState)
admin.site.register(models.ScheduledColorChange)
