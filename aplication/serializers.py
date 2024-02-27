from rest_framework import serializers
from aplication.models import Produto

class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ['id','nome','descricao','preco','quantidade']
