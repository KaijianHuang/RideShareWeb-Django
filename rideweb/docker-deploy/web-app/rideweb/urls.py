"""rideweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from django.contrib.auth import views as auth_views
from users import views as users_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # users side view
    path('', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('intro/', users_views.intro, name = 'intro'),
    path('register/',users_views.register, name='register'),
    path('logout/',auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('profile/', users_views.profile, name='profile'),
    path('RegisterAsDriver/',users_views.RegisterAsDriver,name='RegisterAsDriver'),
    path('driverInterface/',users_views.driver, name = 'driver'),
    path('EditAsUser/', users_views.EditAsUser, name = 'EditAsUser'),
    path('EditAsDriver/', users_views.EditAsDriver, name = 'EditAsDriver'),

    #ride part
    path('CreateRide/', users_views.CreateRide, name = 'CreateRide'),
    path('OwnerEditFail/', users_views.OwnerEditFail, name = 'OwnerEditFail'),
    path('OwnerRides/', users_views.OwnerRides, name = 'OwnerRides'),
    path('OwnerViewEdit/<int:ride_detail_id>/',users_views.OwnerViewEdit,name='OwnerViewEdit'),
    path('edit_ride/',users_views.edit_ride,name='edit_ride'),
    path('SharerViewEdit/<int:ride_detail_id>/', users_views.SharerViewEdit,name = 'SharerViewEdit'),
    path('sharer_edit_ride/',users_views.sharer_edit_ride,name='sharer_edit_ride'),
    path('search_ride/', users_views.search_ride, name = 'search_ride'),
    path('join_ride/', users_views.join_ride, name = 'join_ride'),
    path('driver_search_ride/', users_views.driver_search_ride, name = 'driver_search_ride'),
    path('confirm_ride/<int:ride_detail_id>/', users_views.confirm_ride, name = 'confirm_ride'),
    path('complete_ride/<int:ride_detail_id>/', users_views.complete_ride, name = 'complete_ride'),
    path('ConfirmedDriver/', users_views.ConfirmedDriver, name = 'ConfirmedDriver'),
    path('ConfirmedUser/', users_views.ConfirmedUser, name = 'ConfirmedUser'),
    path('ConfirmedUserDetail/<int:ride_detail_id>/', users_views.ConfirmedUserDetail, name = 'ConfirmedUserDetail'),
    

]
