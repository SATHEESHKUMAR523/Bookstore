from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('books/', views.books, name='books'),
    path('login/', views.login_view, name='login'),
    path('', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('addbook/', views.addbook, name='addbook'),
    path('updatebook/<int:id>/', views.updatebook, name='updatebook'),
    path('deletebook/<int:id>/', views.deletebook, name='deletebook'),
    path("cart/", views.cart, name="cart"),
    path("cart/add/<int:book_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:book_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/clear/", views.clear_cart, name="clear_cart"),
    path("booktable/", views.booktable, name='booktable'),
    path("admin1/", views.admin1, name='admin1'),
    path("search/", views.search_view, name="search"),
    path('contact/', views.contact_page, name='contact'),
    path("cart-payment/", views.cart_payment, name="cart_payment"),
    path("payment-success/", views.payment_success, name="payment_success"),
]