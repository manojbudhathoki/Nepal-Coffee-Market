from django import forms
from .models import Producer, CoffeeProduct

class ProducerProfileForm(forms.ModelForm):
    class Meta:
        model = Producer
        fields = ['tagline', 'description', 'province', 'district', 'municipality', 'address', 'contact_email', 'phone', 'website', 'image_url', 'latitude', 'longitude']
        widgets = {'description': forms.Textarea(attrs={'rows': 5}), 'latitude': forms.NumberInput(attrs={'step': 'any'}), 'longitude': forms.NumberInput(attrs={'step': 'any'})}

class CoffeeProductForm(forms.ModelForm):
    class Meta:
        model = CoffeeProduct
        fields = ['name', 'slug', 'description', 'coffee_type', 'process', 'roast_level', 'origin_altitude_m', 'price_npr', 'unit_label', 'available_for_export', 'in_stock', 'image_url']
        widgets = {'description': forms.Textarea(attrs={'rows': 4}), 'price_npr': forms.NumberInput(attrs={'min': '0', 'step': '0.01'})}

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class RegistrationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        label='Choose your account type',
        help_text='Buyer: discover and review Nepali coffee. Seller: represent a coffee business and request listing ownership. Admin access is never available through public registration.',
        widget=forms.RadioSelect,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'role')

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            UserProfile.objects.update_or_create(
                user=user,
                defaults={'role': self.cleaned_data['role']},
            )
        else:
            self._pending_role = self.cleaned_data['role']
        return user
