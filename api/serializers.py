from rest_framework import serializers

from .models import User, Snippet, Comment
from .utils import generate_uid


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'profile_picture', 'date_joined']
        extra_kwargs = {
            'profile_picture': {'read_only': True},
            'password': {'write_only': True},
            'date_joined': {'read_only': True}
        }

    def create(self, validated_data):
        profile_picture = f"https://avatars.dicebear.com/4.5/api/human/{validated_data.get('username')}.svg"
        validated_data.update({'profile_picture': profile_picture})

        user = User.objects.create_user(**validated_data)
        return user


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Comment
        fields = ['user', 'message', 'timestamp']
        extra_kwargs = {
            'timestamp': {'read_only': True},
            'user': {'read_only': True}
        }

    def create(self, validated_data):
        current_user = self.context.get('request').user
        snippet = Snippet.objects.get(uid=self.context.get('snippet_uid'))
        validated_data.update({'user': current_user, 'snippet': snippet})

        comment = Comment.objects.create(**validated_data)
        return comment


class SnippetSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    comment_set = CommentSerializer(many=True)
    stargazers_count = serializers.ReadOnlyField()

    class Meta:
        model = Snippet
        fields = ['user', 'uid', 'name', 'description', 'content', 'secret', 'stargazers_count', 'comment_set',
                  'created_on',
                  'last_updated']
        extra_kwargs = {
            'user': {'read_only': True},
            'uid': {'read_only': True},
            'created_on': {'read_only': True},
            'last_updated': {'read_only': True}
        }

    def create(self, validated_data):
        current_user = self.context.get('request').user
        uid = generate_uid()
        validated_data.update({'user': current_user, 'uid': uid})

        snippet = Snippet.objects.create(**validated_data)
        return snippet


class UserProfileSerializer(serializers.ModelSerializer):
    snippet_set = SnippetSerializer(many=True)
    stargazers_count = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture', 'stargazers_count', 'snippet_set']
