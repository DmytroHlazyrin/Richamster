from django.urls import path

from .views import BookListCreateView, RandomBookView, index

urlpatterns = [
    path("", index, name="index"),
    path("api/book/", BookListCreateView.as_view(), name="book-list-create"),
    path("api/book/random/", RandomBookView.as_view(), name="book-random"),
]
