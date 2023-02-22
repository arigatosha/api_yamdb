from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'genres', views.GenreViewSet)
router.register(r'titles', views.TitleViewSet)
router.register(r'users', views.UserViewSet, basename='user')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    views.ReviewViewSet, basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    views.CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', views.create_user),
    path('auth/token/', views.Token),
]
