"""terraza URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path

from django.conf import settings
from django.conf.urls.static import static
# from django.conf.urls import url

from booking.views import *
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from rest_framework import permissions
from rest_framework_swagger.views import get_swagger_view


# router = DefaultRouter()
# # router.register('lugares', VenueViewSet, basename='lugares')
# router.register('orders', OrdersView, basename='orders')

schema_view = get_swagger_view(title="Terraza Pineda Booking Documentation APIs")

urlpatterns = [
    path('api/', include('booking.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('djoser.social.urls')),

    #DocumentationSwagger API
    re_path('docs/', schema_view),
]

# urlpatterns += [re_path(r'^.*', TemplateView.as_view(template_name='index.html'))]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)