from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Venue)
admin.site.register(Event)
admin.site.register(Package)
admin.site.register(Extra)
admin.site.register(Rule)
