from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from .models import Area
from .serializers import AreaSerializers, SubsSerializers


class AreaViewSet(CacheResponseMixin,ReadOnlyModelViewSet):
    """"""
    pagination_class = None

    def get_queryset(self):
        if self.action == "list":
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        if self.action=="list":
            return AreaSerializers
        else:
            return SubsSerializers
