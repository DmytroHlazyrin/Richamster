from django.shortcuts import render
from rest_framework import generics
from .models import Book
from .serializers import BookSerializer
import random


class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class RandomBookView(generics.ListAPIView):
    serializer_class = BookSerializer

    def get_queryset(self):
        count = Book.objects.count()
        random_index = random.randint(0, count - 1)
        return Book.objects.filter(pk=Book.objects.all()[random_index].pk)


def index(request):
    return render(request, "index.html")

