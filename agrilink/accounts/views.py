from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import SignupForm, FarmerDetailsForm, LandRequestForm,LandForm
from .models import Profile, FarmerDetails, LandRequest,Land,LandImage


def home(request):
    return render(request, 'landing.html')


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['name']
            )
            Profile.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                user_type=form.cleaned_data['user_type']
            )
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid email or password')

    return render(request, 'login.html')


@login_required
def dashboard(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.user_type == 'farmer':
        return redirect('farmer_dashboard')
    return redirect('landowner_dashboard')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def farmer_dashboard(request):
    profile = get_object_or_404(Profile, user=request.user)

    if profile.user_type != 'farmer':
        return redirect('dashboard')

    farmer = FarmerDetails.objects.filter(user=request.user).first()

    # 🔹 FETCH ALL LANDS ADDED BY LANDOWNERS
    lands = Land.objects.all().prefetch_related('images')

    # 🔹 FETCH FARMER REQUESTS
    requests = LandRequest.objects.filter(farmer=request.user)

    # 🔹 COUNTS FOR STATS
    pending_count = requests.filter(status='pending').count()
    approved_count = requests.filter(status='approved').count()
    cancelled_count = requests.filter(status='cancelled').count()

    if request.method == 'POST':
        # Save farmer details
        if 'save_farmer' in request.POST:
            form = FarmerDetailsForm(request.POST, instance=farmer)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.user = request.user
                obj.save()
                return redirect('farmer_dashboard')

        # Send land request
        if 'send_request' in request.POST:
            land_id = request.POST.get('land_id')
            land = get_object_or_404(Land, id=land_id)

            req_form = LandRequestForm(request.POST)
            if req_form.is_valid():
                req = req_form.save(commit=False)
                req.farmer = request.user
                req.land = land
                req.save()
                return redirect('farmer_dashboard')

    form = FarmerDetailsForm(instance=farmer)
    req_form = LandRequestForm()

    return render(request, 'farmer_dashboard.html', {
        'form': form,
        'req_form': req_form,
        'lands': lands,   # ✅ VERY IMPORTANT
        'requests': requests,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'cancelled_count': cancelled_count,
    })


@login_required
def delete_farmer_details(request, pk):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.user_type != 'farmer':
        return redirect('dashboard')

    farmer = get_object_or_404(FarmerDetails, pk=pk, user=request.user)
    farmer.delete()
    return redirect('farmer_dashboard')


@login_required
def cancel_request(request, pk):
    req = get_object_or_404(LandRequest, pk=pk, farmer=request.user)
    if req.status == 'pending':
        req.status = 'cancelled'
        req.save()
    return redirect('farmer_dashboard')

# land owner dashboard
@login_required
def landowner_dashboard(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.user_type != 'landowner':
        return redirect('dashboard')

    lands = Land.objects.filter(owner=request.user)
    requests = LandRequest.objects.filter(land__owner=request.user)

    land_form = LandForm()

    if request.method == 'POST':

        # ✅ ADD LAND
        if 'add_land' in request.POST:
            land_form = LandForm(request.POST)
            if land_form.is_valid():
                land = land_form.save(commit=False)
                land.owner = request.user
                land.phone = request.user.profile.phone
                land.save()

                # Save images
                for img in request.FILES.getlist('images'):
                    LandImage.objects.create(land=land, image=img)

                messages.success(request, "Land added successfully")
                return redirect('landowner_dashboard')

        # ✅ APPROVE / REJECT REQUEST
        if 'request_id' in request.POST:
            req = get_object_or_404(
                LandRequest,
                pk=request.POST.get('request_id'),
                land__owner=request.user
            )

            if 'approve_request' in request.POST:
                req.status = 'approved'
            elif 'reject_request' in request.POST:
                req.status = 'rejected'

            req.save()
            return redirect('landowner_dashboard')

    return render(request, 'landowner_dashboard.html', {
        'lands': lands,
        'requests': requests,
        'land_form': land_form,
    })


