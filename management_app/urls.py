from django.urls import path
from . import views

app_name = 'management'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('order/update-status/', views.update_order_status, name='update_order_status'),
    path('staff-call/resolve/', views.resolve_staff_call, name='resolve_staff_call'),
    path('receipt/<int:session_id>/', views.print_receipt, name='print_receipt'),
    path('menu/', views.menu_management, name='menu_management'),
    path('menu/create/', views.create_menu_item, name='create_menu_item'),
    path('menu/update/<int:item_id>/', views.update_menu_item, name='update_menu_item'),
    path('menu/delete/<int:item_id>/', views.delete_menu_item, name='delete_menu_item'),
    path('sales/', views.sales_report, name='sales_report'),
    path('users/', views.user_management, name='user_management'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/update/<int:user_id>/', views.update_user, name='update_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
]
