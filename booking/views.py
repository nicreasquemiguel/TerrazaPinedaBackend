from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from rest_framework.viewsets import ModelViewSet
import stripe.error
from .models import Venue, Package, Event, Extra, Rule
from users.models import UserAccount, Profile
from store.models import Cart, CartOrder, CartOrderItem, Tax, Coupon
from .serializers import VenueSerializer, PackageSerializer, EventSerializer, EventCreateSerializer, ExtraSerializer, RuleSerializer, CartSerializer, CartOrderItemSerializer, CartOrderSerializer, DatesOccupiedSerializer, CouponSerializer
from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
import json
from django.conf import settings
import stripe
from decimal import Decimal
from django.db import transaction


stripe.api_key = settings.STRIPE_SECRET_KEY


import datetime
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

        print(payload)
        user_id  = payload['client'] 
        
        #Add default
        admin_id = 1
        venue_id = 1

        advance = 1000


        date  = payload['date']
        #Get package from people 
        people  = payload['people']
        extras = json.loads(payload['extras'])

        ## Get objects
        client = UserAccount.objects.get(id=user_id)
        admin =  UserAccount.objects.get(id=admin_id)
        package = Package.objects.get(n_people=people)
        venue = Venue.objects.get(id=venue_id)

        extrasList = []

        for extra in extras:
            extrasList.append(extra['id'])

        event = Event()
        event.date = date
        event.package = package
        event.client = client
        event.admin = admin
        event.venue = venue
        event.advance = advance
  
        event.save()

        event.extras.add(*extrasList)
        event.save()

        return Response({"message": "Event added successfully", "event_id":event.id}, status=status.HTTP_200_OK)



class EventListAPIView(generics.ListAPIView):
    
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = [AllowAny]



class DatesOccupiedListAPIVIEW(generics.ListAPIView):
    
    queryset = Event.objects.filter(date__gte = datetime.datetime.today()).exclude( status = 'en_carrito')
        
    # queryset = Event.objects.all()
    serializer_class = DatesOccupiedSerializer
    authentication_classes = []
    permission_classes = []


class EventDetailAPIView(generics.RetrieveAPIView):
        
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    authentication_classes = []
    permission_classes = []


class CartAddAPIView(generics.ListCreateAPIView):
    queryset =  Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        payload = request.data
        event_id  =  payload['event_id']
        country = payload['client']    
        cart_id = payload['cart_id']
        user_id = payload['client']
        extras  = payload['extras']
        

        event = Event.objects.get(id=event_id)
        user  = UserAccount.objects.get(id=user_id)
        if user_id != 'undefined':
            user  = UserAccount.objects.get(id=user_id)
        else:
            user = None 
        
        tax = Tax.objects.filter(country=country).first()

        return super().create(request, *args, **kwargs)
    
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
    serializer_class = CartOrderSerializer
    queryset = CartOrder.objects.all()
    # lookup_field = 'oid'
    authentication_classes = []
    permission_classes = []
    # print('somafd')
    # def get_object(self):
    #     order_id = self.kwargs['order_oid']
    #     order = get_object_or_404(CartOrder, oid=order_id)
    #     return order
    
    def create(self, request, *args, **kwargs):


        payload = request.data

        print(payload)

        full_name = payload['full_name']
        email = payload['email']
        phone = payload['phone']
        event_id = payload['event_id']
        # address = payload['address']
        # city = payload['city']
        # state = payload['state']
        # country = payload['country']

        user_id = payload['client']

        # user = UserAccount.objects.get(id=user_id)

        print("user_id ===============", user_id)
        print(payload)
        
        event = Event.objects.get(id=event_id)
        user = UserAccount.objects.get(id=user_id)




        # total_shipping = Decimal(0.0)
        # total_tax = Decimal(0.0)
        # total_service_fee = Decimal(0.0)
        # total_sub_total = Decimal(0.0)
        # total_initial_total = Decimal(0.0)
        # total_total = Decimal(0.0)

        

        order = CartOrder.objects.create(
            # sub_total=total_sub_total,
            # shipping_amount=total_shipping,
            # tax_fee=total_tax,
            # service_fee=total_service_fee,
            buyer=user,
            payment_status="processing",
            full_name=full_name,
            email=email,
            phone=phone,

            event=event
            # buyer=user_id,
            # vendor=user
        #     address=address,
        #     city=city,
        #     state=state,
        #     country=country
        )

        order.save()           
        print(order)
        
        
        if not order:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


        try:
            print('sttrrip')
            checkout_session = stripe.checkout.Session.create(
                customer_email=order.email,
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'mxn',
                            'product_data': {
                                'name': order.full_name,
                            },
                            'unit_amount': int(order.event.package.price * 100),
                        },
                        'quantity': 1,
                    }
                ],
                mode='payment',
                # success_url = f"{settings.SITE_URL}/payment-success/{{order.oid}}/?session_id={{CHECKOUT_SESSION_ID}}",
                # cancel_url = f"{settings.SITE_URL}/payment-success/{{order.oid}}/?session_id={{CHECKOUT_SESSION_ID}}",

                success_url=settings.SITE_URL_FRONTEND+'pago-exitoso/'+ order.oid +'/?session_id={CHECKOUT_SESSION_ID}',
                
                cancel_url=settings.SITE_URL_FRONTEND+'?session_id={CHECKOUT_SESSION_ID}',
            )

            
            order.stripe_session_id = checkout_session['id']
            order.save()

            print(order.stripe_session_id)
            print( checkout_session['id'])
            print( checkout_session.url)
            # return redirect(checkout_session['url'])
            return Response({'url': checkout_session['url']}, status=200)
        except stripe.error.StripeError as e:
            return Response( {'error': f'Something went wrong when creating stripe checkout session: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateOrderAPIView(generics.CreateAPIView):
    serializer_class = CartOrderSerializer
    queryset = CartOrder.objects.all()
    permission_classes = (AllowAny,)
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        payload = request.data

        full_name = payload['full_name']
        email = payload['email']
        phone = payload['phone']
        event_id = payload['event_id']
        # address = payload['address']
        # city = payload['city']
        # state = payload['state']
        # country = payload['country']

        user_id = payload['client']

  

        print("user_id ===============", user_id)
        print(payload)
        
        event = Event.objects.get(id=event_id)
        user = UserAccount.objects.get(id=user_id)

        


        total_shipping = Decimal(0.0)
        total_tax = Decimal(0.0)
        total_service_fee = Decimal(0.0)
        total_sub_total = Decimal(0.0)
        total_initial_total = Decimal(0.0)
        total_total = Decimal(0.0)

        

        order = CartOrder.objects.create(
            # sub_total=total_sub_total,
            # shipping_amount=total_shipping,
            # tax_fee=total_tax,
            # service_fee=total_service_fee,
            buyer=user,
            payment_status="processing",
            full_name=full_name,
            email=email,
            phone=phone,

            event=event
            # buyer=user_id,
            # vendor=user
        #     address=address,
        #     city=city,
        #     state=state,
        #     country=country
        )

            

                

        # order.sub_total=total_sub_total
        # order.shipping_amount=total_shipping
        # order.tax_fee=total_tax
        # order.service_fee=total_service_fee
        # order.initial_total=total_initial_total
        # order.total=total_total

        
        order.save()

        return Response( {"message": "Order Created Successfully", 'order_oid':order.oid}, status=status.HTTP_201_CREATED)


class PaymentSuccessView(generics.RetrieveUpdateAPIView):
    serializer_class = CartOrderSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    queryset = CartOrder.objects.all()
    lookup_field = 'order_id'

    # def get(self, request, order_id):
    #     queryset = self.get_queryset().filter(oid=order_id)
    #     serializer = self.serializer_class(queryset, many=True)
    #     data = serializer.data
    #     return Response({'Message': 'Users active loaded successfully', 'data': data}, status=status.HTTP_201_CREATED)

 
    def update(self, request, *args, **kwargs):
        payload = request.data
        print(payload)
        order_oid = payload['order_oid']
        session_id = payload['session_id']
        
        print(payload)
        order = CartOrder.objects.get(oid=order_oid)
        event = Event.objects.get(id=order.event.id)

        if session_id != 'null':
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == 'paid':
                order.payment_status = 'paid'
                order.save()

                return Response( {"message": "Pago aceptado!", 'order_oid':order}, status=status.HTTP_201_CREATED)
