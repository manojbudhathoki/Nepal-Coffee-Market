from django.db import models
from django.urls import reverse
from django.conf import settings

PROVINCES = [(x, x) for x in ['Koshi Province','Madhesh Province','Bagmati Province','Gandaki Province','Lumbini Province','Karnali Province','Sudurpashchim Province']]
COFFEE_TYPES = [('arabica','Arabica'),('robusta','Robusta'),('blend','Blend'),('specialty','Specialty lot'),('roasted','Roasted coffee'),('green','Green beans')]
PROCESSES = [('washed','Washed'),('natural','Natural / dry'),('honey','Honey'),('anaerobic','Anaerobic'),('mixed','Multiple methods'),('unknown','Not specified')]

class Producer(models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    tagline = models.CharField(max_length=220, blank=True)
    description = models.TextField()
    province = models.CharField(max_length=40, choices=PROVINCES)
    district = models.CharField(max_length=100)
    municipality = models.CharField(max_length=120, blank=True)
    address = models.CharField(max_length=240, blank=True)
    contact_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    website = models.URLField(blank=True, help_text='Official producer website, if available')
    image_url = models.URLField(blank=True, help_text='Optional public image URL for prototype')
    established_year = models.PositiveSmallIntegerField(null=True, blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0, help_text='Editorial directory score; not a verified review average')
    verified = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text='Optional map coordinate')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text='Optional map coordinate')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='coffee_listings')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-featured', '-rating', 'name']
    def __str__(self): return self.name
    def get_absolute_url(self): return reverse('producer_detail', args=[self.slug])

class CoffeeProduct(models.Model):
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=160)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    coffee_type = models.CharField(max_length=20, choices=COFFEE_TYPES, default='arabica')
    process = models.CharField(max_length=20, choices=PROCESSES, default='unknown')
    roast_level = models.CharField(max_length=40, blank=True, help_text='e.g. Light, Medium, Dark, Green')
    origin_altitude_m = models.PositiveSmallIntegerField(null=True, blank=True)
    price_npr = models.DecimalField(max_digits=10, decimal_places=2, help_text='Price in NPR; enter a current confirmed price')
    unit_label = models.CharField(max_length=40, default='250 g')
    available_for_export = models.BooleanField(default=False)
    in_stock = models.BooleanField(default=True)
    image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['price_npr', 'name']
        constraints = [models.UniqueConstraint(fields=['producer','slug'], name='unique_product_slug_per_producer')]
    def __str__(self): return f'{self.name} — {self.producer.name}'

class Recipe(models.Model):
    title = models.CharField(max_length=140)
    slug = models.SlugField(unique=True)
    intro = models.CharField(max_length=250)
    coffee_type = models.CharField(max_length=80, blank=True)
    prep_minutes = models.PositiveSmallIntegerField(default=5)
    ingredients = models.TextField(help_text='One ingredient per line')
    instructions = models.TextField(help_text='One step per line')
    image_url = models.URLField(blank=True)
    published = models.BooleanField(default=True)
    def __str__(self): return self.title

class ProducerEnquiry(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=160)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    def __str__(self): return f'{self.subject} — {self.name}'


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='coffee_favorites')
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','producer'], name='unique_user_producer_favorite')]
    def __str__(self): return f'{self.user} ♥ {self.producer}'

class ProducerReview(models.Model):
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='producer_reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, f'{i} star' if i == 1 else f'{i} stars') for i in range(1,6)])
    title = models.CharField(max_length=120)
    comment = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)
    class Meta:
        ordering = ['-created_at']
        constraints = [models.UniqueConstraint(fields=['producer','user'], name='one_review_per_user_producer')]
    def __str__(self): return f'{self.rating}/5 — {self.producer} by {self.user}'


class ProducerClaim(models.Model):
    STATUS_CHOICES = [('pending','Pending review'),('approved','Approved'),('rejected','Rejected')]
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE, related_name='claims')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='producer_claims')
    business_email = models.EmailField(blank=True)
    proof_note = models.TextField(blank=True, max_length=1500)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ['-created_at']
        constraints = [models.UniqueConstraint(fields=['producer','user'], name='unique_producer_claim_user')]
    def __str__(self): return f'{self.producer} — {self.user} ({self.status})'

class UserProfile(models.Model):
    """Public-site role for an account. Admin access remains controlled by Django is_staff/is_superuser."""
    ROLE_CHOICES = [('buyer', 'Buyer'), ('seller', 'Seller')]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='coffee_profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'

    @property
    def effective_role(self):
        if self.user.is_superuser or self.user.is_staff:
            return 'admin'
        return self.role
