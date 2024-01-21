#urls.py
from django.urls import path
from .views import desk_detail_view,desk_create_view, desk_update_view,desk_delete_view, solid_login_view, dashboard_view, solid_logout_view

urlpatterns = [
    path('create/', desk_create_view, name='desk-create'),
    path('desk/update/<int:desk_id>/', desk_update_view, name='desk-update'),
    path('desk/delete/<int:desk_id>/', desk_delete_view, name='desk-delete'),
    path('desk/<int:desk_id>/', desk_detail_view, name='desk-detail'),
    path('login/', solid_login_view, name='solid-login'),
    path('logout/', solid_logout_view, name='solid-logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    
]