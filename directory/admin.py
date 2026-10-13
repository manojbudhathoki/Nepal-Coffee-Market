from django.contrib import admin
from .models import Producer, CoffeeProduct, Recipe, ProducerEnquiry, Favorite, ProducerReview, ProducerClaim, UserProfile
class ProductInline(admin.TabularInline):
    model = CoffeeProduct
    extra = 0
@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    list_display = ('name','district','province','rating','verified','featured')
    list_filter = ('province','verified','featured')
    search_fields = ('name','district','municipality','description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductInline]
@admin.register(CoffeeProduct)
class CoffeeProductAdmin(admin.ModelAdmin):
    list_display = ('name','producer','coffee_type','process','price_npr','available_for_export','in_stock')
    list_filter = ('coffee_type','process','available_for_export','in_stock','producer__province')
    search_fields = ('name','producer__name','description')
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title','prep_minutes','published')
    list_filter = ('published',)
    prepopulated_fields = {'slug': ('title',)}
@admin.register(ProducerEnquiry)
class ProducerEnquiryAdmin(admin.ModelAdmin):
    list_display = ('subject','name','email','created_at','is_read')
    list_filter = ('is_read','created_at')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user','producer','created_at')

@admin.register(ProducerReview)
class ProducerReviewAdmin(admin.ModelAdmin):
    list_display = ('producer','user','rating','is_published','created_at')
    list_filter = ('rating','is_published')
    search_fields = ('producer__name','user__username','title','comment')

@admin.register(ProducerClaim)
class ProducerClaimAdmin(admin.ModelAdmin):
    list_display = ('producer','user','status','business_email','created_at','reviewed_at')
    list_filter = ('status','created_at')
    search_fields = ('producer__name','user__username','business_email')
    actions = ['approve_claims']
    @admin.action(description='Approve selected claims and link producer listings')
    def approve_claims(self, request, queryset):
        from django.utils import timezone
        approved = 0
        for claim in queryset.select_related('producer'):
            if claim.producer.owner_id and claim.producer.owner_id != claim.user_id:
                continue
            claim.producer.owner = claim.user
            claim.producer.save(update_fields=['owner'])
            claim.status = 'approved'; claim.reviewed_at = timezone.now(); claim.save(update_fields=['status','reviewed_at'])
            approved += 1
        self.message_user(request, f'{approved} producer claim(s) approved.')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')
