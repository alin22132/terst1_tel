from uuid import uuid4

from django.contrib import admin
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from home.models import Category, Brand, Model, Item_list


def index(request):
    # Fetch all categories from the database
    categories = Category.objects.all()

    # Pass the categories to the template
    return render(request, "pages/index.html", {'categories': categories})


def category_detail(request, category_name):
    # Retrieve the category object based on the provided name
    category = get_object_or_404(Category, name=category_name)
    categories = Category.objects.all()

    # Retrieve brands associated with the category
    brands = Brand.objects.filter(category=category)

    # Pass the category and brands objects to the template
    return render(request, 'pages/categories.html', {'category': category, 'brands': brands, 'categories': categories})


def model_list(request, category_name, brand_name):
    # Retrieve the category and brand objects based on the provided names
    category = get_object_or_404(Category, name=category_name)
    brand = get_object_or_404(Brand, name=brand_name)
    categories = Category.objects.all()

    # Retrieve models associated with the category and brand
    models = Model.objects.filter(Brand=brand, Brand__category=category)

    return render(request, 'pages/models.html',
                  {'category': category, 'brand': brand, 'models': models, 'categories': categories})


def items(request, category_name, brand_name, model_name):
    # Retrieve the Category, Brand, and Model objects based on the provided names
    category = get_object_or_404(Category, name=category_name)
    brand = get_object_or_404(Brand, name=brand_name)
    model = get_object_or_404(Model, name=model_name)
    categories = Category.objects.all()

    # Retrieve items based on the provided model name
    item_list = Item_list.objects.filter(Model=model)

    # Pass the items queryset and other parameters to the template for rendering
    return render(request, 'pages/items.html',
                  {'item_list': item_list, 'category': category, 'brand': brand, 'model': model,
                   'categories': categories})


def search_view(request):
    categories = Category.objects.all()[:5]
    query = request.GET.get('q')
    if query:
        results = Item_list.objects.filter(name__icontains=query)
    else:
        results = None
    return render(request, 'pages/search_results.html', {'results': results, 'categories': categories})


def handler404page(request, exception):
    return render(request, 'pages/404.html', status=404)

# TODO Finish the links and then make a post form and thats all (post form to mail, ask for mail)
