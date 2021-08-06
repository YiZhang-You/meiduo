from rest_framework import serializers

from .models import Area


class AreaSerializers(serializers.ModelSerializer):
    """省，市下面的"""
    class Meta:
        model = Area
        fields = ['id', 'name']


class SubsSerializers(serializers.ModelSerializer):
    """市下面的，或者区下的"""
    subs = AreaSerializers(many=True)

    class Meta:
        model = Area
        fields = ['id', 'name', 'subs']
