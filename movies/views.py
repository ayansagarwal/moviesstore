from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required
from django.db.models import Count

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie =  Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html',
        {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id,
        user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def like_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    # Check if the user has already liked this review
    if review.likes.filter(id=request.user.id).exists():
        # User has liked, so unlike it
        review.likes.remove(request.user)
    else:
        # User has not liked, so like it
        review.likes.add(request.user)
    return redirect('movies.show', id=review.movie.id)

def top_reviews(request):
    # Annotate reviews with the count of likes and order by it
    top_reviews_list = Review.objects.annotate(like_count=Count('likes')).order_by('-like_count')

    template_data = {}
    template_data['title'] = 'Top Reviews'
    template_data['reviews'] = top_reviews_list
    return render(request, 'movies/top_reviews.html', {'template_data': template_data})


@login_required
def heart_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    
    is_hearted = False
    if movie.hearts.filter(id=request.user.id).exists():
        # If it exists, remove it
        movie.hearts.remove(request.user)
        is_hearted = False
    else:
        # If it doesn't exist, add it
        movie.hearts.add(request.user)
        is_hearted = True

    # This is the key part: check for a header sent by JavaScript
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'hearted': is_hearted})

    # Fallback for non-JavaScript requests
    return redirect(request.META.get('HTTP_REFERER', 'movies.index'))


@login_required
def hearted_movies_list(request):
    """
    Displays a list of all movies the current user has hearted.
    """
    # Get all movies hearted by the current user
    hearted_movies = request.user.hearted_movies.all()
    
    template_data = {}
    template_data['title'] = 'My Hearted Movies'
    template_data['movies'] = hearted_movies
    return render(request, 'movies/hearted_movies.html', {'template_data': template_data})