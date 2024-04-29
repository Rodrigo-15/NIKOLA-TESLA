from rest_framework import serializers
from desk.models import Headquarter


class HeadquarterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Headquarter
        fields = "__all__"
