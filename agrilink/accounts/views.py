from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import SignupForm, FarmerDetailsForm, LandRequestForm,LandForm,ProductForm,ProductRequestForm
from .models import Profile, FarmerDetails, LandRequest,Land,LandImage,Product,ProductRequest,ProductImage


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
    elif profile.user_type == 'landowner':
        return redirect('landowner_dashboard')
    else:
        return redirect('customer_dashboard')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def farmer_dashboard(request):
    profile = get_object_or_404(Profile, user=request.user)

    if profile.user_type != 'farmer':
        return redirect('dashboard')

    farmer = FarmerDetails.objects.filter(user=request.user).first()

    lands = Land.objects.all().prefetch_related('images')
    requests = LandRequest.objects.filter(farmer=request.user)

    products = Product.objects.filter(farmer=request.user)

    pending_count = requests.filter(status='pending').count()
    approved_count = requests.filter(status='approved').count()
    cancelled_count = requests.filter(status='cancelled').count()

    product_form = ProductForm()

    if request.method == 'POST':

        # SAVE FARMER PROFILE
        if 'save_farmer' in request.POST:
            form = FarmerDetailsForm(request.POST, instance=farmer)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.user = request.user
                obj.save()
                return redirect('farmer_dashboard')

        # ADD PRODUCT
        if 'add_product' in request.POST:
            product_form = ProductForm(request.POST)
            if product_form.is_valid():
                product = product_form.save(commit=False)
                product.farmer = request.user
                product.save()

                # Save multiple images
                for img in request.FILES.getlist('images'):
                    ProductImage.objects.create(
                        product=product,
                        image=img
                    )

                messages.success(request, "Product added successfully")
                return redirect('farmer_dashboard')

        # SEND LAND REQUEST
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
        'lands': lands,
        'requests': requests,
        'products': products,
        'product_form': product_form,
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

        #  ADD LAND
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

        #  APPROVE / REJECT REQUEST
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

# delete land
@login_required
def delete_land(request, pk):
    profile = get_object_or_404(Profile, user=request.user)

    # Only landowners allowed
    if profile.user_type != 'landowner':
        return redirect('dashboard')

    land = get_object_or_404(Land, pk=pk, owner=request.user)

    land.delete()
    messages.success(request, "Land deleted successfully")

    return redirect('landowner_dashboard')

# Customer dasboard
@login_required
def customer_dashboard(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.user_type != 'customer':
        return redirect('dashboard')

    products = Product.objects.all()
    requests = ProductRequest.objects.filter(customer=request.user)
    req_form = ProductRequestForm()

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        req_form = ProductRequestForm(request.POST)
        if req_form.is_valid():
            req = req_form.save(commit=False)
            req.customer = request.user
            req.product = product
            req.save()
            return redirect('customer_dashboard')

    return render(request, 'customer_dashboard.html', {
        'products': products,
        'requests': requests,
        'req_form': req_form,
    })

