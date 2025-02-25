from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(PaymentOrder)
admin.site.register(Review)
admin.site.register(Coupon)
admin.site.register(BookingFAQ)
admin.site.register(Tax)