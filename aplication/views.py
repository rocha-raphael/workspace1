from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Produto
from .serializers import ProdutoSerializer

# Create your views here.
def produtos(request):
    return HttpResponse("HELLO WORLD!")


class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    
@api_view(['GET','POST'])
def lista_produtos(request):    
    if request.method == "GET":
        prod = Produto.objects.all()
        serial = ProdutoSerializer(prod, many=True)
        return Response(serial.data, status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET','PUT','POST','DELETE'])
def change_delete_produtos(request, pk):
    try:
        prod_pk = Produto.objects.get(pk=pk)
    except Produto.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
#        prods = Produto.objects.all()
#        serial = ProdutoSerializer(prods, many=True)
        serial = ProdutoSerializer(prod_pk)
        return Response(serial.data)
    elif request.method == "PUT":
#        serial = ProdutoSerializer(data=request.data)
        serial = ProdutoSerializer(prod_pk,data=request.data)
        if serial.is_valid():
            serial.save()
            return Response(serial.data)#, status=status.HTTP_201_CREATED)
        else:
            return Response(serial.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "POST":
        serial = ProdutoSerializer(data=request.data)
#        prod = Produto.objects.all()
#        serial = ProdutoSerializer(prod)
        if serial.is_valid():
            serial.save()
            return Response(serial.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serial.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        prod_pk.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#@api_view(['GET','POST'])
#def lista_produtos(request):    
#    pass
