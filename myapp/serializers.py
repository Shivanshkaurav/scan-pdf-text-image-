from rest_framework import serializers
from .models import Summary

class SummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = '__all__'
        
class PdfSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=None)
    images = serializers.ImageField()