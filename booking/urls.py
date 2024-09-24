from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from users.views import ProfileView


router = DefaultRouter()
# router.register('lugares', VenueViewSet, basename='lugares')
router.register(r'mis-eventos/(?P<eid>.+)/orders', OrdersView)


urlpatterns = [
    # path('', views.home, name='home'),
    path('', include(router.urls)),
    path('sitios/', VenueListAPIView.as_view()),
    path('paquetes/', PackageViewSet.as_view({'get': 'list'})),
    path('extras/', ExtraListAPIView.as_view()),
    path('eventos/', EventListAPIView.as_view()),
    path('add-event/', EventCreateApiView.as_view()),
    path('approve/<eid>/', EventApproveAPIView.as_view())
    path('eventos/ocupados/', DatesOccupiedListAPIVIEW.as_view()),
    path('eventos/<eid>', MyEventAPIView.as_view()),
    path('user/profile/<user_id>/', ProfileView.as_view(), name='user_profile'),
    path('rules/', RuleListAPIView.as_view(), na me='rules'),
    path('sitios-activos', VenueActiveListAPIView.as_view()),
    path('sitios/<slug>/', VenueDetailAPIView.as_view()),

    path('mis-eventos/', MyEventsAPIView.as_view()),
    path('reviews/', RatingAPIView.as_view()),
    path('reviews/<id>/', ReviewRetrieveViewAPI.as_view()),
    
    path('checkout/<int:pk>', CheckoutAPIView.as_view()),
    path('coupons/<code>', CouponAPIView.as_view()),
    path('stripe-checkout/', StripeCheckoutAPI.as_view(), name='stripe-checkout'),
    path('pago-exitoso/<oid>/', PaymentSuccessView.as_view(), name='payment-success'),

]
