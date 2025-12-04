from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    path('', views.start_session, name='start_session'),
    path('session/create/', views.create_session, name='create_session'),
    path('menu/', views.menu_list, name='menu_list'),
    path('submit/', views.submit_order, name='submit_order'),
    path('history/', views.order_history, name='order_history'),
    path('call-staff/', views.call_staff, name='call_staff'),
    path('call-staff/submit/', views.submit_staff_call, name='submit_staff_call'),
    path('payment/', views.payment, name='payment'),
]
