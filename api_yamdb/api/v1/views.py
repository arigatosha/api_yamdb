# from django.shortcuts import render
from reviews.models import Category, Genre, Title
from rest_framework import filters, viewsets
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from .mixins import CreateListDestroyViewSet
from .permissions import IsAdminOrReadOnly
from .serializers import CategorySerializer, GenreSerializer, TitleSerializer, OnlyReadTitleSerializer

class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        Avg("reviews__score")
    ).order_by("name")
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category','genre','name','year')


    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return OnlyReadTitleSerializer
        return TitleSerializer

