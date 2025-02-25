from django.db import models

from django.dispatch import receiver
from django.db.models.signals import post_save
from shortuuid.django_fields import ShortUUIDField
import uuid
from django.utils.text import slugify
from users.models import UserAccount, Profile
from booking.models import Event, Package
# Create your models here.
 

class PaymentOrder(models.Model):
    PAYMENT_STATUS = (
        ("pagado", "Pagado"),
        ("pendiente","Pendiente"),
        ("procesando", "Procesando"),
        ("cancelled", "Cancelled"),
    )


    PAYMENT_TYPES = (
        ("stripe", "Pago por Stripe"),
        ("deposito", "Deposito Bancario"),
        ("transferencia", "Transferncia Bancaria"),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True)
    vendor = models.ForeignKey(UserAccount,on_delete=models.PROTECT, related_name="vendor", blank=True)
    payer = models.ForeignKey(UserAccount, on_delete=models.PROTECT, null=True, related_name="payer", blank=True)

    oid = ShortUUIDField(unique=True, length=10, alphabet='abcdefg12345')
    created = models.DateTimeField(auto_now_add = True)

    subtotal = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    tax_fee = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)

    linked = models.BooleanField(default=False)
    payment_status = models.CharField(choices=PAYMENT_STATUS, max_length=100, default="pending")
    payment_type = models.CharField(choices=PAYMENT_TYPES, max_length=100)
    stripe_session_id = models.CharField(max_length=1000, null=True, blank=True)
    
    def __str__(self):
        return str(self.event.date) + self.oid 

    def save(self, *args, **kwargs):
        if self.payment_status == "pagado" and self.linked == False:

            self.event.advance += float(self.subtotal)
                        
            print('saviend')
            self.event.save()
            self.linked = True
            # event = Event.objects.get(eid = self.event.eid)
            # event.advance += float(self.subtotal)

        if self.subtotal:
            self.tax_fee = (float(self.subtotal) * 0.16)
            self.total = float(self.subtotal) + self.tax_fee
            
        super(PaymentOrder, self).save(*args, **kwargs) 

class BookingFAQ(models.Model):
    product = models.CharField(max_length=1000)
    question = models.CharField(max_length=1000)
    answer = models.CharField(max_length=1000)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.question
    
    class Meta:
        verbose_name_plural = 'Preguntas Frecuentes'


class Review(models.Model):
    RATING = (
        (1, "1 Estrella"),
        (2, "2 Estrellas"),
        (3, "3 Estrellas"),
        (4, "4 Estrellas"),
        (5, "5 Estrellas"),
    )
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    review = models.TextField()
    reply = models.TextField(null=True, blank=True)
    rating = models.PositiveIntegerField(default=None, choices=RATING)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Review del " +  str(self.event.date)
    
    class Meta:
        verbose_name_plural = 'Opinión de Eventos'

    def profile(self):
        return Profile.objects.get(user=self.user)
    
@receiver(post_save, sender=Review)
def update_event_rating(sender, instance, **kwargs):
    if instance.event: 
        instance.event.save()

# class Notification(models.Model):
#     user = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name="user")
#     vendor = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name='vendor_noti')
#     order = models.ForeignKey(CartOrder, on_delete=models.SET_NULL, null=True, blank=True)
#     order_item = models.ForeignKey(CartOrderItem, on_delete=models.SET_NULL, null=True, blank=True)
#     seen = models.BooleanField(default=False)
#     date = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name_plural = "Notification"
    
#     # Method to return a string representation of the object
#     def __str__(self):
#         if self.order:
#             return self.order.oid
#         else:
#             return "Notification"

class Coupon(models.Model):
    vendor = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True, related_name="coupon_vendor")
    used_by = models.ManyToManyField(UserAccount, blank=True)
    code = models.CharField(max_length=1000)
    discount = models.IntegerField(default=1)
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    # ShortUUID field
    cid = ShortUUIDField(length=10, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz")
    
    # Method to calculate and save the percentage discount
    def save(self, *args, **kwargs):
        new_discount = int(self.discount) / 100
        self.get_percent = new_discount
        super(Coupon, self).save(*args, **kwargs) 
    

    def __str__(self):
        return self.code
    
    class Meta:
        ordering =['-id']



class Tax(models.Model):
    country = models.CharField(max_length=255)
    rate = models.IntegerField(default=5, help_text="En porcentajes 5%")
    active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.country 

    class Meta: 
        # pass
        verbose_name_plural = 'Taxes'
        ordering = ['country']

