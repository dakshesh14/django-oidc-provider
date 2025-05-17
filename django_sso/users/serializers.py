from django.contrib.auth import get_user_model

# rest framework
from rest_framework import serializers

User = get_user_model()


class TokenRequestSerializer(serializers.Serializer):
    client_id = serializers.CharField(max_length=152)
    client_secret = serializers.CharField(max_length=256)
    code = serializers.CharField(max_length=256)
    redirect_uri = serializers.URLField()
    grant_type = serializers.ChoiceField(choices=[("authorization_code", "authorization_code")])
