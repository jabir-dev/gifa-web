from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response

from shop.forms import ReviewForm, SignupForm, SigninForm
from shop.models import Product, Category
from shop.serializer import ProductSerializer

from django.core.paginator import Paginator

def home(request):
    # if request.META['HTTP_HOST'] != "ecommerce.hem.xyz.np":
    #     return redirect("http://ecommerce.hem.xyz.np")
    products = Product.objects.filter(active=True)[:10]
    categories = Category.objects.filter(active=True)[:5]
    context = {"products": products, "categories": categories}
    return render(request, "shop/home.html", context)



def search(request):
    q = request.GET["q"]
    products = Product.objects.filter(active=True, name__icontains=q)
    categories = Category.objects.filter(active=True)
    context = {"products": products,
               "categories": categories,
               "title": q + " - search"}
    return render(request, "shop/list.html", context)


def categories(request, slug):
    cat = Category.objects.get(slug=slug)
    products = Product.objects.filter(active=True, category=cat)
    categories = Category.objects.filter(active=True)

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')  # new
    page_obj = paginator.get_page(page_number)  # changed
    
    context = {"products":products, "categories":categories, "title":cat.name + " - Categories", "page_obj": page_obj}
    return render(request, "shop/list.html", context)


def detail(request, slug):
    product = Product.objects.get(active=True, slug=slug)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Review saved")
        else:
            messages.error(request, "Invalid form")
    else:
        form = ReviewForm()


    categories = Category.objects.filter(active=True)
    context = {"product" : product,
               "categories":categories,
               "form": form}
    return render(request, "shop/detail.html", context)




def checkout(request):
    request.session.pop('data', None)
    return redirect("/")

def about(request):
    return render(request, "shop/about.html")

def contact(request):
    return render(request, "shop/contact.html")

@api_view(['GET'])
def api_products(request):
    query = request.GET.get("q", "")
    products = Product.objects.filter(Q(name__contains=query) | Q(description__contains=query))
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)
