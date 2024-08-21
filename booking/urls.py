from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from users.views import ProfileView



urlpatterns = [
    # path('', views.home, name='home'),
    path('sitios/', VenueListAPIView.as_view()),
    path('paquetes/', PackageViewSet.as_view({'get': 'list'})),
    path('extras/', ExtraListAPIView.as_view()),
    path('eventos/', EventListAPIView.as_view()),
    path('add-event/', EventCreateApiView.as_view()),
    path('eventos/ocupados/', DatesOccupiedListAPIVIEW.as_view()),
    path('eventos/<int:pk>', MyEventAPIView.as_view()),
    path('user/profile/<user_id>/', ProfileView.as_view(), name='user_profile'),
    path('rules/', RuleListAPIView.as_view(), name='rules'),
    path('sitios-activos', VenueActiveListAPIView.as_view()),
    path('sitios/<slug>/', VenueDetailAPIView.as_view()),

    path('mis-eventos/', MyEventsAPIView.as_view()),

    #Store endpoints
    path('cart-view/', CartAddAPIView.as_view()),
    path('create-order/', CreateOrderAPIView.as_view()),
    path('orders/<oid>/', CartOrderDetailView.as_view()),

    path('checkout/<int:pk>', CheckoutAPIView.as_view()),
    path('coupons/<code>', CouponAPIView.as_view()),
    path('stripe-checkout/', StripeCheckoutAPI.as_view(), name='stripe-checkout'),
    path('pago-exitoso/<oid>/', PaymentSuccessView.as_view(), name='payment-success'),

]
