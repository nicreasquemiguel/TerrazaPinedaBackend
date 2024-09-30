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
        user_id  = payload['user_id'] 
        
        #Add default
        admin_id = 1
        venue_id = 1

        advance = 1000


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

        extrasList = []

        for extra in extras:
            extrasList.append(extra['id'])

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


class EventApproveAPIView(generics.UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (IsAdminUser,)
    lookup_field = 'eid'
    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)

    #     if getattr(instance, '_prefetched_objects_cache', None):
    #         # If 'prefetch_related' has been applied to a queryset, we need to
    #         # forcibly invalidate the prefetch cache on the instance.
    #         instance._prefetched_objects_cache = {}

    #     return Response(serializer.data)

class EventAdminStatisticsAPIView(generics.ListAPIView):
    serializer_class = EventsStatiticsAdminSerializer
    permission_classes = (IsAdminUser,)
    
    def get_queryset(self):
        print(self)
        admin_id = self.get('admin')
        admin = UserAccount.objects.get(id=admin_id)
        today = datetime.now()
        events_to_approve = Event.objects.get(status="solicitud").count()
        event_count_month = Event.objects.filter(date__month = today.month, date__year = today.year ).exclude(status = "solicitud").exclude( status = "cancelado").exclude(status = "rechazado").count()
        event_count_year = Event.objects.filter(date__year = today.year ).exclude(status = "solicitud").exclude( status = "cancelado").exclude(status = "rechazado").count()
    
        
        return [{
            "events_to_approve": events_to_approve,
            "event_count_month": event_count_month,
            "event_count_year" : event_count_year, 
        }]
    
    def list(self):
        queryset = self.get_queryset()
        serializer  = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        
    

class DatesOccupiedListAPIVIEW(generics.ListAPIView):
    
    queryset = Event.objects.filter(date__gte = datetime.datetime.today()).exclude( status = 'en_carrito')
        
    # queryset = Event.objects.all()
    serializer_class = DatesOccupiedSerializer
    authentication_classes = []
    permission_classes = []


class EventDetailAPIView(generics.RetrieveAPIView):
        
    queryset = Event.objects.all()
    serializer_class = EventSerializer
 


# class CartAddAPIView(generics.ListCreateAPIView):
#     queryset =  Cart.objects.all()
#     serializer_class = CartSerializer
#     permission_classes = []

#     def create(self, request, *args, **kwargs):
#         payload = request.data
#         event_id  =  payload['event_id']
#         country = payload['client']    
#         cart_id = payload['cart_id']
#         user_id = payload['client']
#         extras  = payload['extras']
        

#         event = Event.objects.get(id=event_id)
#         user  = UserAccount.objects.get(id=user_id)
#         if user_id != 'undefined':
#             user  = UserAccount.objects.get(id=user_id)
#         else:
#             user = None 
        
#         tax = Tax.objects.filter(country=country).first()

#         return super().create(request, *args, **kwargs)
    


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
        print(payload)

        # full_name = payload['full_name']
        # email = payload['email']
        # phone = payload['phone']
        event_id = payload['event_id']
        payment_type = 'stripe'
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





        # total_tax = Decimal(0.0)
        total_sub_total = Decimal(payload['subtotal'])
        # total_initial_total = Decimal(0.0)
        # total_total = Decimal(0.0)

        

        order = PaymentOrder.objects.create(
            # sub_total=total_sub_total,
            # shipping_amount=total_shipping,
            # tax_fee=total_tax,
            # service_fee=total_service_fee,
            payer=user,
            payment_status="procesando",
            payment_type=payment_type,
            subtotal = total_sub_total,

            # full_name=full_name,
            # email=email,
            # phone=phone,

            event=event,
            # buyer=user_id,
            vendor=user,
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
            print('final')
            
            order.stripe_session_id = checkout_session['id']
            order.save()

            # print(order.stripe_session_id)
            # print( checkout_session['id'])
            # print( checkout_session.url)
            # return redirect(checkout_session['url'])
            return Response({'url': checkout_session['url']}, status=200)
        except stripe.error.StripeError as e:
            return Response( {'error': f'Something went wrong when creating stripe checkout session: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentSuccessView(generics.RetrieveUpdateAPIView):
    serializer_class = PaymentOrderSerializer
    queryset = PaymentOrder.objects.all()
    lookup_field = 'oid'

    permission_classes = [AllowAny]
    authentication_classes = []
 

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
        # print(self.request.user.id)
        print(self.request.__dict__)
        print(self.request.data)
        print(self.kwargs)
        return PaymentOrder.objects.all().filter(payer = self.request.user.id).filter(event__eid = self.kwargs['eid'])


class MyEventsAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    queryset = Event.objects.all()


    def get_queryset(self):

        return Event.objects.all().filter(client = self.request.user.id)


class MyEventAPIView(generics.RetrieveAPIView):
    serializer_class = EventSerializer
    # queryset = Event.objects.all()
    lookup_field = 'eid'
    
    # def get(self, request, *args, **kwargs):
    #     return self.retrieve(request, *args, **kwargs)

    def get_object(self):

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
