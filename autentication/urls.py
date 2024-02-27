from django.urls import path, include
from .views import *

#router = DefaultRouter()
#router.register(r'produtos', ProdutoViewSet)

urlpatterns = [
    path('', index.as_view(), name='index'),
    path('usuarios/', usuarios.as_view(), name='usuarios')
]
