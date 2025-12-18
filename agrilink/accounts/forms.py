from django import forms
from .models import FarmerDetails, LandRequest,Land


class SignupForm(forms.Form):
    name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=15)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    user_type = forms.ChoiceField(
        choices=[('farmer', 'Farmer'), ('landowner', 'Landowner')]
    )


class FarmerDetailsForm(forms.ModelForm):
    class Meta:
        model = FarmerDetails
        fields = [
            'farmer_name',
            'phone',
            'email',
            'experience_years',
            'field_experience',
            'description',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class LandRequestForm(forms.ModelForm):
    class Meta:
        model = LandRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }


# land form
class LandForm(forms.ModelForm):
    class Meta:
        model = Land
        fields = [
            'farm_name',
            'soil_type',
            'suitable_for',
            'location',
            'description',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }