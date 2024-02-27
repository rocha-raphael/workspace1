from django.db import models

# Create your models here.
class Produto(models.Model):
    nome = models.CharField(max_length=255, verbose_name='Nome')
    descricao = models.TextField(verbose_name='Descrição', blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço')
    quantidade = models.IntegerField(default=0, verbose_name='Quantidade em Estoque')

    def __str__(self):
        return self.nome

class Categoria(models.Model):
    nome = models.CharField(max_length=100, verbose_name='Nome')
    descricao = models.TextField(verbose_name='Descrição', blank=True, null=True)

    def __str__(self):
        return self.nome
