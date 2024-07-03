from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(CartOrder)
admin.site.register(Cart)
admin.site.register(CartOrderItem)
admin.site.register(Notification)
admin.site.register(Review)
admin.site.register(Coupon)
admin.site.register(BookingFAQ)
admin.site.register(Tax)