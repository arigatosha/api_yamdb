import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'


class OnlyReadTitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        source='reviews__score__avg', read_only=True
    )
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class MyTokenObtainPairSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email',)

    def validate_username(self, value):
        regex = re.compile(r'^[\w.@+-]+')
        if not regex.match(value):
            raise serializers.ValidationError('Недоспустимые символы')
        if value == 'me':
            raise ValidationError('Недоспустимое имя ')
        elif User.objects.filter(username=value).exists():
            raise ValidationError('Неверная авторизация')
        return value


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                {
                    'username':
                        'Нельзя использовать me в качестве имени пользователя.'
                }
            )
        match = re.fullmatch(r'^[\w.@+-]+', str(value))
        if match is None:
            raise serializers.ValidationError('Недоспустимые символы')
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = Review
        fields = (
            'id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        if not self.context.get('request').method == 'POST':
            return data
        author = self.context.get('request').user
        title_id = self.context.get('view').kwargs.get('title_id')
        if Review.objects.filter(author=author, title=title_id).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на это произведение'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = Comment
        fields = (
            'id', 'text', 'author', 'pub_date')
