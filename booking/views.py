from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
import stripe.error
from .models import Venue, Package, Event, Extra, Rule
from users.models import UserAccount, Profile
from store.models import Tax, Coupon, PaymentOrder, Review
from .serializers import VenueSerializer, PackageSerializer, EventSerializer, EventCreateSerializer, ExtraSerializer, RuleSerializer,   DatesOccupiedSerializer, CouponSerializer, PaymentOrderSerializer, ReviewSerializer, EventsStatiticsAdminSerializer
from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework import status
from rest_framework.response import Response
import json
from django.forms.models import model_to_dict
from django.conf import settings
import stripe
import mercadopago
from decimal import Decimal
from rest_framework.filters import OrderingFilter
import requests
from django_filters.rest_framework import DjangoFilterBackend



from environs import Env 
stripe.api_key = settings.STRIPE_SECRET_KEY


env = Env()
env.read_env()


from datetime import datetime, timedelta


class VenueListAPIView(generics.ListCreateAPIView):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer

    authentication_classes = []
    permission_classes = []

class VenueActiveListAPIView(generics.ListAPIView):
    queryset = Venue.objects.filter(active=True)
    serializer_class = VenueSerializer

    authentication_classes = []
    permission_classes = []

class VenueDetailAPIView(generics.RetrieveAPIView):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    lookup_field = 'slug'
    
    authentication_classes = []
    permission_classes = []

class RuleListAPIView(generics.ListAPIView):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer
    
    permission_classes = []

class PackageViewSet(ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    
    authentication_classes = []
    permission_classes = []

class ExtraListAPIView(generics.ListAPIView):
    queryset = Extra.objects.all()
    serializer_class = ExtraSerializer
    
    authentication_classes = []
    permission_classes = []
    

class EventCreateApiView(generics.CreateAPIView):
    serializer_class = EventCreateSerializer
    
    authentication_classes = []
    permission_classes = []
    
    
    def create(self, request, *args, **kwargs):
        payload = request.data
        user_id  = payload['user_id'] 
        
        admin_id = 1
        venue_id = 1

        date  = payload['date']
        
        #Get package from people 
        people  = payload['people']
        description  = payload['description']
        extras = json.loads(payload['extras'])

        ## Get objects
        client = UserAccount.objects.get(id=user_id)
        admin =  UserAccount.objects.get(id=admin_id)
        package = Package.objects.get(n_people=people)
        venue = Venue.objects.get(id=venue_id)

        extrasList = extras
 
        event = Event()
        event.date = date
        event.package = package
        event.client = client
        event.description = description
        event.admin = admin
        event.venue = venue
        event.save()

        event.extras.add(*extrasList)
        event.save()

        return Response({"message": "Event added successfully", "eid":event.eid}, status=status.HTTP_200_OK)



class EventListAPIView(generics.ListAPIView):
    
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = [AllowAny]
    filter_backends = [OrderingFilter]
    ordering_fields = ('-date',)

class EventApproveAPIView(generics.UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (IsAdminUser,)
    lookup_field = 'eid'


class EventAdminStatisticsAPIView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventsStatiticsAdminSerializer
    permission_classes = (IsAdminUser,)
    
    def get_queryset(self):
        today = datetime.now()
        lastMonth = today - timedelta(days=datetime.now().day)
        lastYear = today - timedelta(days=datetime.now().day)
        
        events_to_approve = Event.objects.filter(status="solicitud").count()

        event_count_month = Event.objects.filter(date__month = today.month, date__year = today.year ).exclude(status = "solicitud").exclude( status = "cancelado").exclude(status = "rechazado").count()
        event_count_last_month = Event.objects.filter(date__month = lastMonth.month, date__year = lastMonth.year ).exclude(status = "solicitud").exclude( status = "cancelado").exclude(status = "rechazado").count()

        event_count_year = Event.objects.filter(date__year = today.year ).exclude(status = "solicitud").exclude( status = "cancelado").exclude(status = "rechazado").count()
        event_count_last_year = Event.objects.filter(date__year = today.year - 1 ).exclude(status = "solicitud").exclude( status = "cancelado").exclude(status = "rechazado").count()
        
    

        
        qs = {
            "events_to_approve": events_to_approve,
            "event_count_month": event_count_month,
            "event_count_last_month" : event_count_last_month,
            "event_count_year" : event_count_year,
            "event_count_last_year" : event_count_last_year, 
        }
        print(qs)
        
        return [ qs ]
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer  = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        
    

class DatesOccupiedListAPIVIEW(generics.ListAPIView):
    queryset = Event.objects.filter(date__gte = datetime.today()).exclude( status = 'en_carrito').order_by("-date")

    serializer_class = DatesOccupiedSerializer
    authentication_classes = []
    permission_classes = []
    filter_backends = [OrderingFilter]
    ordering_fields = ('date',)

class EventDetailAPIView(generics.RetrieveAPIView):
        
    queryset = Event.objects.all()
    serializer_class = EventSerializer
 


class CheckoutAPIView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    lookup_field = 'pk'
    serializer_class = EventSerializer
    authentication_classes = []
    permission_classes = []


class CouponAPIView(generics.RetrieveAPIView):
    queryset = Coupon.objects.all()
    lookup_field = 'code'
    serializer_class = CouponSerializer
    authentication_classes = []
    permission_classes = []


class StripeCheckoutAPI(generics.CreateAPIView):
    serializer_class = PaymentOrder
    queryset = PaymentOrder.objects.all()
    authentication_classes = []
    permission_classes = []
    
    def create(self, request, *args, **kwargs):
        payload = request.data
        event_id = payload['event_id']
        payment_type = 'stripe'
        user_id = payload['client']
        event = Event.objects.get(eid=event_id)
        user = UserAccount.objects.get(id=user_id)

        total_sub_total = Decimal(payload['subtotal'])

        order = PaymentOrder.objects.create(
            payer=user,
            payment_status="procesando",
            payment_type=payment_type,
            subtotal = total_sub_total,

            event=event,
            vendor=user,
        )

        order.save()           

        
        if not order:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


        try:
            checkout_session = stripe.checkout.Session.create(
                customer_email=order.payer.email,
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'mxn',
                            'product_data': {
                                'name': order.payer.get_full_name(),
                                'description':  order.oid + 'la fecha: ' + str(event.date),
                                
                            },
                            'unit_amount': int(order.total * 100),
                        },
                        'quantity': 1,
                    }
                ],
                mode='payment',
                success_url=settings.SITE_URL_FRONTEND+'mis-eventos/'+order.event.eid + '/ordenes/'+ order.oid +'/?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=settings.SITE_URL_FRONTEND+'mis-eventos/'+order.event.eid + '?session_id={CHECKOUT_SESSION_ID}',
            )

            
            order.stripe_session_id = checkout_session['id']
            order.save()

            return Response({'url': checkout_session['url']}, status=200)
        except stripe.error.StripeError as e:
            return Response( {'error': f'Something went wrong when creating stripe checkout session: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MercadoPagoPreferenceAPIView(generics.CreateAPIView):
    serializer_class = PaymentOrder
    queryset = PaymentOrder.objects.all()
    authentication_classes = []
    permission_classes = []
    
    def create(self, request, *args, **kwargs):
        payload = request.data
        user_id = payload['client']
        event_id = payload['event_id']
        amount = payload['amount']


        event = Event.objects.get(eid=event_id)
        user = UserAccount.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)
        
        order = PaymentOrder.objects.create(
            payer=user,
            payment_status="procesando",
            payment_type="mercardo pago",
            subtotal = amount,

            event=event,
            vendor=user,
        )

        order.save()           

        sdk = mercadopago.SDK(env("MERCADO_ACCESS_KEY"))

        preference_data = {
        "items": [
            {
            "id": f'EID-{event.eid}',
            "title": f'Pago del evento: {event.date}',
            "description": f'Adelanto para el evento del {event.date}',
            "category_id": "car_electronics",
            "quantity": 1,
            "currency_id": "MXN",
            "unit_price": amount
            }
        ],
        "payer": {
            "name": user.first_name,
            "surname": user.last_name,
            "email": user.email,
            "phone": {
                "area_code": "52",
                "number": user.phone
            }

        },

        "back_urls": {
            "success": f'http://http://192.168.100.15:5173/mis-eventos/{event.eid}/ordenes/{order.oid}/',
            "pending": f'http://localhost:5173/mis-eventos/{event.eid}/',
            "failure": f'http://localhost:5173/mis-eventos/{event.eid}/',

        # "notification_url": "https://www.your-site.com/ipn",
        "statement_descriptor": "TERRAZAPINEDA",
        "external_reference": f'Reference_{order.oid}',
        "expires": True,

        "metadata": None
        }
        }
        

        
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        
        return Response({"preference":preference}, status=200)


class MercadoPagoNotificationAPIView(generics.CreateAPIView):
    serializer_class = PaymentOrder
    queryset = PaymentOrder.objects.all()
    authentication_classes = []
    permission_classes = []
    
    def create(self, request, *args, **kwargs):
        payload = request.data

        sdk = mercadopago.SDK(env("MERCADO_ACCESS_KEY"))
        order = PaymentOrder.objects.get(oid=payload['orderID'])
        
        headers = {"Authorization": f'Bearer {env("MERCADO_ACCESS_KEY")}'}
        res = requests.get(f'https://api.mercadopago.com/merchant_orders/{payload["mercadoID"]}', headers=headers) 
        res_dict = res.json()

        if(res_dict["status"] == "closed"):
            order.payment_status = "pagado"
            order.save()
        
        return Response({"Orden pagada por medio de Mercado Pago"}, status=200)
    
class PaymentSuccessView(generics.RetrieveUpdateAPIView):
    serializer_class = PaymentOrderSerializer
    queryset = PaymentOrder.objects.all()
    lookup_field = 'oid'

    permission_classes = [AllowAny]
    authentication_classes = []
    
        
    def patch(self, request, *args, **kwargs):

        payload = request.data
        order = PaymentOrder.objects.get(oid=payload["oid"])

        request.get()
        order.payment_status 


        return Response({"message": "Profile changed successfully"}, status=status.HTTP_200_OK)
 

class OrdersView(ModelViewSet):
    serializer_class = PaymentOrderSerializer
    queryset = PaymentOrder.objects.all()
    lookup_field = 'oid'
    lookup_fields = ['oid']

    authentication_classes = (JWTAuthentication,)
    permission_classes = [AllowAny]

    def get_object(self):
        queryset = self.get_queryset()                          # Get the base queryset
        queryset = self.filter_queryset(queryset)               # Apply any filter backends
        multi_filter = {field: self.kwargs[field] for field in self.lookup_fields}
        obj = get_object_or_404(queryset, **multi_filter)       # Lookup the object
        self.check_object_permissions(self.request, obj)
        return obj


    def get_queryset(self):
        return PaymentOrder.objects.all().filter(payer = self.request.user.id).filter(event__eid = self.kwargs['eid'])


class MyEventsAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    queryset = Event.objects.all()


    def get_queryset(self):
        status = self.request.query_params.get('status')
        return Event.objects.all().filter(client = self.request.user.id, status=status)


class MyEventAPIView(generics.RetrieveAPIView):
    serializer_class = EventSerializer
    lookup_field = 'eid'
    


    def get_object(self):
        print(self.kwargs)
        obj = Event.objects.get(eid = self.kwargs['eid'])
        if obj.client == self.request.user:
            self.check_object_permissions(self.request, obj)
            return obj


class RatingAPIView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    authentication_classes = (JWTAuthentication,)
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        payload = request.data


        eid = payload["event"]
        review = payload["review"]
        ratings = payload["rating"]
        user_id  = request.user.id

        event = Event.objects.get(eid=eid)
        user = UserAccount.objects.get(id=user_id)

        if event.event_rating or event.event_review:
            rating = event.review_set.all()[0]
        else:
            rating = Review()

        rating.rating = ratings
        rating.review = review
        rating.user = user
        rating.event = event
        rating.active = True
        rating.save()
        return Response({"message": "Review/Rating added successfully", "review": review}, status=status.HTTP_200_OK)


    def get_queryset(self):
        return Review.objects.all().filter(user = self.request.user.id)


class ReviewRetrieveViewAPI(generics.RetrieveUpdateAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    authentication_classes = (JWTAuthentication,)
    permission_classes = [AllowAny]


    def get_queryset(self):
        return Review.objects.all().filter(user = self.request.user.id)
