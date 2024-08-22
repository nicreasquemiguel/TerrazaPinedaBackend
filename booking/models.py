from django.db import models
import datetime


from django.dispatch import receiver
from django.db.models.signals import post_save
from shortuuid.django_fields import ShortUUIDField
import uuid
from django.utils.text import slugify
from users.models import UserAccount, Profile
# import store.models as store


ICON_TYPE= (
    ("Bootstrap Icons", "Bootstrap Icons"),
    ("Fontawesome Icons", "Fontawesome Icons"),
    ("Box Icons", "Box Icons"),
    ("Remi Icons", "Remi Icons"),
    ("Flat Icons", "Flat Icons")
)

class Package(models.Model):
    n_people = models.IntegerField(default=30)
    price = models.FloatField()
    title = models.CharField(max_length = 255, blank = True)
    description = models.TextField()
    hours = models.TextField()
    icon = models.CharField(max_length=100, blank=True)

    class Meta:
       ordering = ('n_people',)
    def __str__(self):
        return self.title + " de " + str(self.n_people) + " personas"

class Extra(models.Model):
    title = models.CharField(max_length = 255, blank = True)
    description = models.TextField()
    price = models.FloatField()

    def __str__(self):
        return self.title

class Rule(models.Model):
    title = models.CharField(max_length = 255)
    desciption = models.CharField(max_length = 255) 
    
    def __str__(self):
        return self.title

class Venue(models.Model):
    name = models.CharField(max_length = 255, blank = True)
    address = models.CharField(max_length = 255, blank = True)
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique = True, default="")
    
    def __str__(self):
        return self.name
    
    def __save__(self, *args, **kwargs):
        if self.slug == "" or self.slug is None:
            self.slug = slugify(self.name)
        
        super(Venue, self).save(*args, **kwargs)



ta = datetime.time(10,00,00)
td = datetime.time(00,00,00)

class Event(models.Model):

    # STATUS = (
    #     ("en_carrito", "En carrito"),
    #     ("en_revision", "En revisión"),
    #     ("aceptado","Aceptado"),
    #     ("rechazado", "Rechazado"),
    #     ("finalizado", "Finalizado"),
    # )

    STATUS = (
        ("solicitud", "Solicitud de Reserva"),
        ("aceptacion", "Aceptación de Reserva"),
        ("apartado", "Apartado inicial"),
        ("liquidado", "Monto liquidado"),
        ("entregado", "Entregado"),
        ("en_curso", "En curso"),
        ("finalizado", "Reserva finalizada"),
        ("cancelado", "Reserva cancelada"),
        ("rechazado", "Rechazado"),
    )
 
    date = models.DateField()
    id = models.AutoField( primary_key=True )
    arrival = models.TimeField(default = ta)
    departure = models.TimeField(default = td)
    package = models.ForeignKey(Package, on_delete= models.PROTECT, related_name= "package")
    extras =  models.ManyToManyField(Extra,  blank=True)
    client = models.ForeignKey(UserAccount, on_delete= models.PROTECT, related_name= "client")
    admin = models.ForeignKey(UserAccount, on_delete= models.PROTECT, related_name= "admin")
    venue = models.ForeignKey(Venue, on_delete = models.PROTECT, related_name = "venue")
    created = models.DateTimeField(auto_now_add = True)
    modified = models.DateTimeField(auto_now = True)
    advance = models.FloatField(default = 0)
    status = models.CharField(max_length=100, choices=STATUS, default="solicitud")
    rating = models.PositiveIntegerField(default =0,  blank=True)
    rating_comment = models.CharField(max_length = 255, null = True,  blank=True)
    slug = models.SlugField(unique = True, default="")
    payment_intent = models.CharField(max_length=1000, null=True, blank=True)
    # eid = ShortUUIDField(default=uuid.uuid4, length=10, alphabet='abcdefg12345')
    description = models.TextField(default='', null= False )

    @property
    def total_price(self):
        total = 0
        total = self.package.price 
        for extra in self.extras:
            total += extra.price 
        

        return total
        

    # Calculates the average rating of the product
    def event_rating(self):
        from store.models import Review
        event_rating = Review.objects.filter(event=self).aggregate(avg_rating=models.Avg('rating'))
        return event_rating['avg_rating']
    

    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(str(self.client.id) + '-' + self.date) 
        
        if self.status == 'en_carrito':
            pass
                
        # self.rating = self.event_rating()
        
        super(Event, self).save(*args, **kwargs)

    def __str__(self):
        return self.client.first_name + " " + self.client.last_name + " el " + str(self.date)   


    class Meta:
        ordering = ['-date']

class VenueFeatures(models.Model):
    hotel = models.ForeignKey(Venue, on_delete=models.CASCADE)
    icon_type = models.CharField(max_length=100, null=True, blank=True, choices=ICON_TYPE)
    icon = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.name)


