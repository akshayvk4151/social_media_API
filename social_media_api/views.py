from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ImageSerializer, PostCreateSerializer, UserRegister, PostSerializer
from .models import Post
from . import models
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum
from .serializers import UserSerializer
from rest_framework import status

#Api for registering a user
@api_view(['POST'])
def register(request, format=None):
    serializer = UserRegister(data=request.data)
    data = {}
    if serializer.is_valid():
        account = serializer.save()
        data['response'] = 'registered'
        data['username'] = account.username
        data['email'] = account.email
        token, created = Token.objects.get_or_create(user=account)
        data['token'] = token.key
    else:
        data = serializer.errors
    return Response(data)

#Api for creating a post.
@api_view(['POST'])
def create_post(request, format=None):
    serializer = PostCreateSerializer(data=request.data)
    if serializer.is_valid():
        post = serializer.save()
        return Response({'message': 'Post created successfully.'})
    return Response(serializer.errors, status=400)


#Pagination
class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100




#Api for retrieving a list of posts for the authenticated user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def post_list(request, format=None):
    user = request.user
    liked_posts = user.liked_posts.all()
    disliked_posts = user.disliked_posts.all()

    similar_liked_posts = Post.objects.filter(tags__in=liked_posts.values('tags')).exclude(id__in=liked_posts.values('id'))
    similar_disliked_posts = Post.objects.filter(tags__in=disliked_posts.values('tags')).exclude(id__in=disliked_posts.values('id'))

    posts = list(similar_liked_posts) + list(similar_disliked_posts)
    posts.sort(key=lambda x: (x.tags.filter(id__in=liked_posts.values('tags')).aggregate(weight_sum=Sum('weight'))['weight_sum'], x.created_date), reverse=True)

    paginator = CustomPagination()
    paginated_posts = paginator.paginate_queryset(posts, request)

    data = []
    for post in paginated_posts:
        # Serialize the images field
        images_data = ImageSerializer(post.images.all(), many=True).data
        
        post_data = {
            'id': post.id,
            'description': post.description,
            'images': images_data, 
            'likes_count': post.likes.count(),
            'dislikes_count': post.dislikes.count(),
            'created_date': post.created_date,
            'is_liked': user in post.likes.all(),
            'is_disliked': user in post.dislikes.all()
        }
        data.append(post_data)

    return paginator.get_paginated_response(data)



# API for liking a post
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, id, format=None):
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        return Response({'message': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    user = request.user
    post.likes.add(user)
    post.dislikes.remove(user)
    return Response({'message': 'Post liked'})


# API for disliking a post
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def dislike_post(request, id, format=None):
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        return Response({'message': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    user = request.user
    post.likes.remove(user)
    post.dislikes.add(user)
    return Response({'message': 'Post disliked'})





# API allows users to get a list of the users who have liked a post.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def post_liked_users(request, id, format=None):
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        return Response({'message': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
    
    liked_users = post.likes.all()
    serializer = UserSerializer(liked_users, many=True)
    return Response(serializer.data)