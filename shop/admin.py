from django.contrib import admin
from .models import Book,BestSeller,Admin,ContactMessage

# Register your models here.

admin.site.register(Book)
admin.site.register(BestSeller)
admin.site.register(Admin)
admin.site.register(ContactMessage)