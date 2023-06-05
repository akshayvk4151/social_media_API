from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Image, Tag
from django.contrib.auth.models import User

User = get_user_model()

class UserRegister(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "email", "password2"]

    def save(self):
        reg = User(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'password does not match'})
        reg.set_password(password)
        reg.save()
        return reg


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name', 'weight']


class PostSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    liked_by_current_user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'description', 'images', 'likes', 'dislikes', 'created_date', 'tags', 'likes_count',
                  'dislikes_count', 'liked_by_current_user']
        read_only_fields = ['likes', 'dislikes', 'created_date', 'likes_count', 'dislikes_count', 'liked_by_current_user']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_dislikes_count(self, obj):
        return obj.dislikes.count()

    def get_liked_by_current_user(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
            return obj.likes.filter(id=user.id).exists()
        return False
    


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class PostCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(child=serializers.ImageField(), write_only=True)
    tags = serializers.ListField(child=TagSerializer(), write_only=True)

    class Meta:
        model = Post
        fields = ['description', 'images', 'tags']

    def create(self, validated_data):
        images_data = validated_data.pop('images')
        tags_data = validated_data.pop('tags')

        post = Post.objects.create(**validated_data)

        for image_data in images_data:
            Image.objects.create(post=post, image=image_data)

        for tag_data in tags_data:
            tag = Tag.objects.create(**tag_data)
            post.tags.add(tag)

        return post