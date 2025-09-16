from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg # Import Avg

# Create your models here.
class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')
    hearts = models.ManyToManyField(User, related_name='hearted_movies', blank=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    def __str__(self):
        return str(self.id) + ' - ' + self.name
    
class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie,
        on_delete=models.CASCADE)
    user = models.ForeignKey(User,
        on_delete=models.CASCADE)
    
    likes = models.ManyToManyField(User, related_name='liked_reviews', blank=True)
    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name
    
class Rating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.IntegerField(choices=[(i, i) for i in range(1, 6)]) # 1 to 5 stars

    class Meta:
        # Ensures a user can only rate a specific movie once
        unique_together = ('movie', 'user')

    def save(self, *args, **kwargs):
        # Call the original save method first
        super().save(*args, **kwargs)
        
        # After saving a rating, recalculate and update the movie's average rating
        # We access the related movie through the 'movie' foreign key
        movie_ratings = self.movie.ratings.all()
        self.movie.average_rating = movie_ratings.aggregate(Avg('stars'))['stars__avg']
        self.movie.save()