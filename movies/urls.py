from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='movies.index'),
    path('<int:id>/', views.show, name='movies.show'),
    path('<int:id>/review/create/', views.create_review,
        name='movies.create_review'),
    path('<int:id>/review/<int:review_id>/edit/',
        views.edit_review, name='movies.edit_review'),
    path('<int:id>/review/<int:review_id>/delete/',
        views.delete_review, name='movies.delete_review'),
    path('review/<int:review_id>/like/', views.like_review, name='movies.like_review'),
    path('top-reviews/', views.top_reviews, name='movies.top_reviews'),
    path('<int:movie_id>/heart/', views.heart_movie, name='movies.heart'),
    path('hearted/', views.hearted_movies_list, name='movies.hearted_list'),
    path('movies/<int:id>/rate/', views.add_rating, name='movies.add_rating'),
]