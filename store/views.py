from .serializers import *
from .models import *
from rest_framework import generics, permissions, status
from rest_framework.response import Response
#import pagination
from rest_framework.pagination import PageNumberPagination

class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all().exclude(name="Extraction")
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = PageNumberPagination
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)


class CategoryListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    pagination_class = PageNumberPagination

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        category = Category.objects.get(slug=category_slug)
        products = Product.objects.filter(category=category, Status=True)
        return products
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
