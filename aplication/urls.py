#from .my_project import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

#router = DefaultRouter()
#router.register(r'produtos', ProdutoViewSet)

urlpatterns = [
    path('produtos/', produtos, name='produtos'),
    path('lista/<int:pk>', change_delete_produtos, name='lista_del'),
    path('lista/', lista_produtos, name='lista'),
#    path('lista/', change_delete_produtos, name='lista'),
#    path('', include(router.urls)),
]
