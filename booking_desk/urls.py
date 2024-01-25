from django.urls import path
from . import views

app_name = 'booking_desk'

urlpatterns = [

    path('book/<int:desk_id>/', views.book_desk_view, name='book-desk'),
]