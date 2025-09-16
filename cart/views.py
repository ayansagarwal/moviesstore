from django.shortcuts import render

from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item
from django.contrib.auth.decorators import login_required

from django.db.models import Sum

def index(request):
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids != []):
        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart, movies_in_cart)
    template_data = {}
    template_data['title'] = 'Cart'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total
    return render(request, 'cart/index.html',
        {'template_data': template_data})
def add(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('home.index')

def add_to_cart(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('cart.index')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')

@login_required
def purchase(request):
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids == []):
        return redirect('cart.index')
    movies_in_cart = Movie.objects.filter(id__in=movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)
    order = Order()
    order.user = request.user
    order.total = cart_total
    order.save()
    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        item.quantity = cart[str(movie.id)]
        item.save()
    request.session['cart'] = {}
    template_data = {}
    template_data['title'] = 'Purchase confirmation'
    template_data['order_id'] = order.id
    return render(request, 'cart/purchase.html',
        {'template_data': template_data})

@login_required
def subscription_level_view(request):
    """
    Calculates the total amount a user has spent and determines their
    subscription level.
    """
    # 1. Filter all orders belonging to the currently logged-in user.
    user_orders = Order.objects.filter(user=request.user)

    # 2. Calculate the sum of the 'total' field from those orders.
    #    The .get() method provides a default value of 0 if the user has no orders.
    total_spent = user_orders.aggregate(Sum('total')).get('total__sum', 0)

    # 3. Handle the case where a user has no purchases (sum is None).
    if total_spent is None:
        total_spent = 0

    # 4. Determine the subscription level based on the total amount spent.
    if total_spent > 30:
        level = "Premium"
        emoji = "🌟"
    elif total_spent >= 15:
        level = "Medium"
        emoji = "👍"
    else:
        level = "Basic"
        emoji = "😊"

    # 5. Pass the data to the template.
    context = {
        'total_spent': total_spent,
        'subscription_level': level,
        'emoji': emoji,
    }

    return render(request, 'cart/subscription_page.html', context)