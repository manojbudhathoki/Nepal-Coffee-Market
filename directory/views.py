from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from functools import wraps
from django.db.models import Q, Avg
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from .models import Producer, CoffeeProduct, Recipe, PROVINCES, COFFEE_TYPES, PROCESSES, ProducerEnquiry, Favorite, ProducerReview, ProducerClaim
from .forms import ProducerProfileForm, CoffeeProductForm, RegistrationForm
from .models import UserProfile

def home(request):
    featured = Producer.objects.filter(featured=True)[:3]
    if not featured.exists(): featured = Producer.objects.all()[:3]
    products = CoffeeProduct.objects.select_related('producer').filter(in_stock=True)[:4]
    return render(request, 'directory/home.html', {'featured': featured, 'products': products, 'producer_count': Producer.objects.count(), 'product_count': CoffeeProduct.objects.count()})

def producer_list(request):
    qs = Producer.objects.all().prefetch_related('products')
    q=request.GET.get('q','').strip(); province=request.GET.get('province',''); district=request.GET.get('district','').strip(); coffee_type=request.GET.get('coffee_type',''); process=request.GET.get('process',''); verified=request.GET.get('verified',''); min_rating=request.GET.get('min_rating',''); min_price=request.GET.get('min_price','').strip(); max_price=request.GET.get('max_price','').strip(); sort=request.GET.get('sort','recommended'); export=request.GET.get('export',''); stock=request.GET.get('stock','')
    if q: qs=qs.filter(Q(name__icontains=q)|Q(description__icontains=q)|Q(district__icontains=q)|Q(municipality__icontains=q)|Q(products__name__icontains=q)).distinct()
    if province in dict(PROVINCES): qs=qs.filter(province=province)
    if district: qs=qs.filter(Q(district__icontains=district)|Q(municipality__icontains=district))
    if verified=='1': qs=qs.filter(verified=True)
    if export=='1': qs=qs.filter(products__available_for_export=True).distinct()
    if stock=='1': qs=qs.filter(products__in_stock=True).distinct()
    if min_rating:
        try: qs=qs.filter(rating__gte=max(Decimal('0'),min(Decimal(min_rating),Decimal('5'))))
        except (InvalidOperation, ValueError): pass
    if coffee_type in dict(COFFEE_TYPES): qs=qs.filter(products__coffee_type=coffee_type,products__in_stock=True).distinct()
    if process in dict(PROCESSES): qs=qs.filter(products__process=process,products__in_stock=True).distinct()
    try:
        if min_price: qs=qs.filter(products__price_npr__gte=max(Decimal('0'),Decimal(min_price)),products__in_stock=True).distinct()
        if max_price: qs=qs.filter(products__price_npr__lte=max(Decimal('0'),Decimal(max_price)),products__in_stock=True).distinct()
    except (InvalidOperation, ValueError): pass
    sort_map={'rating':'-rating','price_low':'products__price_npr','price_high':'-products__price_npr','name':'name','newest':'-created_at','recommended':'-featured'}
    qs=qs.order_by(sort_map.get(sort,'-featured'),'-rating','name').distinct()
    return render(request,'directory/producers.html',{'producers':qs,'provinces':PROVINCES,'coffee_types':COFFEE_TYPES,'processes':PROCESSES,'filters':request.GET,'result_count':qs.count()})

def producer_detail(request, slug):
    producer = get_object_or_404(Producer, slug=slug)
    products = producer.products.all()

    # Public visitors see published reviews only. A signed-in buyer can also
    # see their own review if it is awaiting moderation, so they can edit it.
    public_reviews = producer.reviews.filter(is_published=True).select_related('user')
    own_review = None
    if request.user.is_authenticated:
        own_review = producer.reviews.filter(user=request.user).first()
        if own_review and not own_review.is_published:
            reviews = (public_reviews | producer.reviews.filter(pk=own_review.pk)).select_related('user').distinct()
        else:
            reviews = public_reviews
    else:
        reviews = public_reviews

    average = public_reviews.aggregate(avg=Avg('rating'))['avg']
    is_favorite = request.user.is_authenticated and Favorite.objects.filter(
        user=request.user, producer=producer
    ).exists()
    return render(request, 'directory/producer_detail.html', {
        'producer': producer,
        'products': products,
        'reviews': reviews,
        'review_average': average,
        'is_favorite': is_favorite,
        'own_review': own_review,
        'already_reviewed': own_review is not None,
    })

def coffee_guide(request): return render(request,'directory/coffee_guide.html',{'coffee_types':COFFEE_TYPES,'processes':PROCESSES})
def recipe_list(request): return render(request,'directory/recipes.html',{'recipes':Recipe.objects.filter(published=True)})
def about(request): return render(request,'directory/about.html')
def coffee_history(request): return render(request,'directory/history.html')
def contact(request):
    if request.method=='POST':
        name=request.POST.get('name','').strip(); email=request.POST.get('email','').strip(); subject=request.POST.get('subject','').strip(); message=request.POST.get('message','').strip()
        try:
            validate_email(email)
            email_valid=True
        except ValidationError:
            email_valid=False
        if not all([name,email,subject,message]) or not email_valid or len(message)>5000:
            messages.error(request,'Please enter a valid email and complete every field. Messages must be under 5,000 characters.')
        else:
            ProducerEnquiry.objects.create(name=name,email=email,subject=subject,message=message); messages.success(request,'Thank you. Your message has been sent to the directory team.')
            return redirect('contact')
    return render(request,'directory/contact.html')

def _effective_role(user):
    """Return the account's effective role. Only Django staff/superusers are admins."""
    if user.is_superuser or user.is_staff:
        return 'admin'
    profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': 'buyer'})
    # Do not silently promote a normal account to staff/admin based on profile data.
    return profile.role if profile.role in {'buyer', 'seller'} else 'buyer'


def _role_home(user):
    role = _effective_role(user)
    if role == 'admin':
        return redirect('/admin/')
    if role == 'seller':
        return redirect('producer_dashboard')
    return redirect('buyer_dashboard')


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(request, *args, **kwargs):
            role = _effective_role(request.user)
            if role not in allowed_roles:
                messages.error(request, 'This page is not available for your account type.')
                return _role_home(request.user)
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


@role_required('buyer')
def buyer_dashboard(request):
    return render(request, 'directory/buyer_dashboard.html', {
        'favorites': Producer.objects.filter(favorited_by__user=request.user).distinct()[:6],
        'reviews': ProducerReview.objects.filter(user=request.user).select_related('producer')[:5],
        'account_role': 'Buyer',
    })


def register(request):
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Your {user.coffee_profile.get_role_display().lower()} account is ready. Welcome to Nepali Coffee!')
        return _role_home(user)
    return render(request, 'directory/auth_form.html', {
        'form': form, 'heading': 'Create your account', 'button': 'Create account', 'is_registration': True,
    })


def user_login(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return _role_home(user)
    return render(request, 'directory/auth_form.html', {
        'form': form, 'heading': 'Welcome back', 'button': 'Log in', 'is_registration': False,
    })


@require_POST
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@role_required('buyer')
@require_POST
def toggle_favorite(request, slug):
    producer = get_object_or_404(Producer, slug=slug)
    obj, created = Favorite.objects.get_or_create(user=request.user, producer=producer)
    if not created:
        obj.delete()
        messages.info(request, 'Removed from your saved producers.')
    else:
        messages.success(request, 'Producer saved to your favourites.')
    return redirect(producer.get_absolute_url())


@role_required('buyer')
@require_POST
def submit_review(request, slug):
    producer = get_object_or_404(Producer, slug=slug)
    raw_rating = request.POST.get('rating', '')
    title = request.POST.get('title', '').strip()
    comment = request.POST.get('comment', '').strip()
    try:
        rating = int(raw_rating)
    except (ValueError, TypeError):
        rating = 0

    if rating not in range(1, 6) or not title or len(title) > 120 or not comment or len(comment) > 2000:
        messages.error(request, 'Please provide a title (up to 120 characters), a comment (up to 2,000 characters), and a rating from 1 to 5.')
        return redirect(producer.get_absolute_url() + '#reviews')

    # Fetch the current user's review first, then update that exact row. This
    # avoids creating duplicates and preserves moderation status on edits.
    review = ProducerReview.objects.filter(producer=producer, user=request.user).first()
    if review is None:
        ProducerReview.objects.create(
            producer=producer,
            user=request.user,
            rating=rating,
            title=title,
            comment=comment,
        )
        messages.success(request, 'Your review has been submitted.')
    else:
        review.rating = rating
        review.title = title
        review.comment = comment
        review.save(update_fields=['rating', 'title', 'comment'])
        messages.success(request, 'Your review has been updated.')
    return redirect(producer.get_absolute_url() + '#reviews')


@role_required('buyer')
def favourites(request):
    return render(request, 'directory/favourites.html', {
        'producers': Producer.objects.filter(favorited_by__user=request.user).distinct()
    })


@role_required('seller')
def producer_dashboard(request):
    producer = Producer.objects.filter(owner=request.user).first()
    claims = request.user.producer_claims.select_related('producer')
    return render(request, 'directory/producer_dashboard.html', {
        'producer': producer,
        'claims': claims,
        'products': producer.products.all() if producer else CoffeeProduct.objects.none(),
        'account_role': 'Seller',
    })

@role_required('seller')
@require_POST
def claim_producer(request,slug):
    producer=get_object_or_404(Producer,slug=slug)
    if producer.owner_id: messages.error(request,'This producer listing is already linked to an account.')
    else:
        claim,created=ProducerClaim.objects.get_or_create(producer=producer,user=request.user,defaults={'business_email':request.POST.get('business_email','').strip(),'proof_note':request.POST.get('proof_note','').strip()[:1500]})
        if created: messages.success(request,'Your claim request has been submitted for administrator review. Access is not granted until it is approved.')
        elif claim.status=='pending': messages.info(request,'Your claim is already awaiting review.')
        else: messages.info(request,f'Your previous claim status is: {claim.get_status_display()}. Contact us if you need help.')
    return redirect('producer_dashboard')

# Producer portal actions. Editing is permitted only after an administrator has
# linked the approved producer claim to the signed-in account.
def _owned_producer_or_redirect(request):
    producer = Producer.objects.filter(owner=request.user).first()
    if producer is None:
        messages.error(request, 'Your producer claim must be approved before you can manage a listing.')
        return None
    return producer

@role_required('seller')
def edit_producer_profile(request):
    producer = _owned_producer_or_redirect(request)
    if producer is None:
        return redirect('producer_dashboard')
    form = ProducerProfileForm(request.POST or None, request.FILES or None, instance=producer)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Your producer profile has been updated.')
        return redirect('producer_dashboard')
    return render(request, 'directory/model_form.html', {'form': form, 'heading': 'Edit producer profile', 'button': 'Save profile'})

@role_required('seller')
def add_product(request):
    producer = _owned_producer_or_redirect(request)
    if producer is None:
        return redirect('producer_dashboard')
    form = CoffeeProductForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        product = form.save(commit=False)
        product.producer = producer
        product.save()
        messages.success(request, 'Your coffee product has been added.')
        return redirect('producer_dashboard')
    return render(request, 'directory/model_form.html', {'form': form, 'heading': 'Add a coffee product', 'button': 'Add product'})

@role_required('seller')
def edit_product(request, product_id):
    producer = _owned_producer_or_redirect(request)
    if producer is None:
        return redirect('producer_dashboard')
    product = get_object_or_404(CoffeeProduct, pk=product_id, producer=producer)
    form = CoffeeProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Your coffee product has been updated.')
        return redirect('producer_dashboard')
    return render(request, 'directory/model_form.html', {'form': form, 'heading': 'Edit coffee product', 'button': 'Save product'})

@role_required('seller')
@require_POST
def delete_product(request, product_id):
    producer = _owned_producer_or_redirect(request)
    if producer is None:
        return redirect('producer_dashboard')
    product = get_object_or_404(CoffeeProduct, pk=product_id, producer=producer)
    product.delete()
    messages.success(request, 'The product listing has been deleted.')
    return redirect('producer_dashboard')
