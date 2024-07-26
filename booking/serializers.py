from rest_framework import serializers
from .models import Venue, Package, Event, Extra, Rule
from store.models import Cart, CartOrder, CartOrderItem, BookingFAQ, Coupon, Review, Notification
from django.contrib.auth import get_user_model
from users.serializers import UserCreateSerializer, ProfileSerializer
from users.models import UserAccount


User = get_user_model()

class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }

class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = '__all__'

class ExtraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extra
        fields = '__all__'


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    # package = serializers.CharField(source='package.title')

    # client = serializers.
    class Meta:
        model = Event
        fields = '__all__'
        # depth = 1
        lookup_field = 'eid'
        extra_kwargs = {
            'url': {'lookup_field': 'eid'}
        }

    def __init__(self, *args, **kwargs):
        super(EventSerializer, self).__init__(*args, **kwargs)
        # Customize serialization depth based on the request method.
        request = self.context.get('request')
        if request and request.method == 'POST':
            # When creating a new product, set serialization depth to 0.
            self.Meta.depth = 0
        else:
            # For other methods, set serialization depth to 3.
            self.Meta.depth = 1


class EventCreateSerializer(serializers.ModelSerializer):
    people = serializers.IntegerField()
    class Meta:
        model = Event
        fields = ['people','date','venue','client','admin']


class MyEventsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Event


class DatesOccupiedSerializer(serializers.ModelSerializer):
    # package = serializers.CharField(source='package.title')

    # client = serializers.
    class Meta:
        model = Event
        fields = ['date']
        # depth = 1





class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(CartSerializer, self).__init__(*args, **kwargs)
        # Customize serialization depth based on the request method.
        request = self.context.get('request')
        if request and request.method == 'POST':
            # When creating a new cart order item, set serialization depth to 0.
            self.Meta.depth = 0
        else:
            # For other methods, set serialization depth to 3.
            self.Meta.depth = 3


# Define a serializer for the CartOrderItem model
class CartOrderItemSerializer(serializers.ModelSerializer):
    # Serialize the related Product model
    # product = ProductSerializer()  

    class Meta:
        model = CartOrderItem
        fields = '__all__'
      
    def __init__(self, *args, **kwargs):
        super(CartOrderItemSerializer, self).__init__(*args, **kwargs)
        # Customize serialization depth based on the request method.
        request = self.context.get('request')
        if request and request.method == 'POST':
            # When creating a new cart order item, set serialization depth to 0.
            self.Meta.depth = 0
        else:
            # For other methods, set serialization depth to 3.
            self.Meta.depth = 3

            # Define a serializer for the CartOrder model
class CartOrderSerializer(serializers.ModelSerializer):
    # Serialize related CartOrderItem models
    orderitem = CartOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = CartOrder
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CartOrderSerializer, self).__init__(*args, **kwargs)
        # Customize serialization depth based on the request method.
        request = self.context.get('request')
        if request and request.method == 'POST':
            # When creating a new cart order, set serialization depth to 0.
            self.Meta.depth = 0
        else:
            # For other methods, set serialization depth to 3.
            self.Meta.depth = 3


# Define a serializer for the ProductFaq model
class BookingFAQSerializer(serializers.ModelSerializer):
    # Serialize the related Product model
    event = EventSerializer()

    class Meta:
        model = BookingFAQ
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BookingFAQSerializer, self).__init__(*args, **kwargs)
        # Customize serialization depth based on the request method.
        request = self.context.get('request')
        if request and request.method == 'POST':
            # When creating a new product FAQ, set serialization depth to 0.
            self.Meta.depth = 0
        else:
            # For other methods, set serialization depth to 3.
            self.Meta.depth = 3


class VendorSerializer(serializers.ModelSerializer):
    # Serialize related CartOrderItem models
    user = UserCreateSerializer(read_only=True)

    class Meta:
        model = UserAccount
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(VendorSerializer, self).__init__(*args, **kwargs)
        # Customize serialization depth based on the request method.
        request = self.context.get('request')
        if request and request.method == 'POST':
            # When creating a new cart order, set serialization depth to 0.
            self.Meta.depth = 0
        else:
            # For other methods, set serialization depth to 3.
            self.Meta.depth = 3

class ReviewSerializer(serializers.ModelSerializer):
    # Serialize the related Product model
    product = EventSerializer()
    profile = ProfileSerializer()
    
    class Meta:
        model = Review
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ReviewSerializer, self).__init__(*args, **kwargs)
        # Customize serialization depth based on the request method.
        request = self.context.get('request')
        if request and request.method == 'POST':
            # When creating a new review, set serialization depth to 0.
            self.Meta.depth = 0
        else:
            # For other methods, set serialization depth to 3.
            self.Meta.depth = 3
 
 
 
class CouponSerializer(serializers.ModelSerializer):

    class Meta:
        model = Coupon
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CouponSerializer, self).__init__(*args, **kwargs)
        # Customize serialization depth based on the request method.
        request = self.context.get('request')
        if request and request.method == 'POST':
            # When creating a new coupon, set serialization depth to 0.
            self.Meta.depth = 0
        else:
            # For other methods, set serialization depth to 3.
            self.Meta.depth = 3


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(NotificationSerializer, self).__init__(*args, **kwargs)
        # Customize serialization depth based on the request method.
        request = self.context.get('request')
        if request and request.method == 'POST':
            # When creating a new coupon user, set serialization depth to 0.
            self.Meta.depth = 0
        else:
            # For other methods, set serialization depth to 3.
            self.Meta.depth = 3


