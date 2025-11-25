from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'role', 'department', 'designation']
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ['role']


    def create(self, validated_data):
        password = validated_data.pop('password')
        validate_password(password)
        user = User(**validated_data)
        user.set_password(raw_password=password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('department', None)
        validated_data.pop('designation', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            validate_password(password)
            instance.set_password(password)

        instance.save()
        return instance


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)