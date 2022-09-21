from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product
from cart.forms import CartAddProductForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rolepermissions.roles import assign_role
from django.contrib import messages
from django.urls import reverse
from . forms import ProductAddForm, CategoryAddForm, UserRegistrationForm
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template.loader import render_to_string
from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required
def add_user_view(request):
    if request.user.has_perm('create_stuff'):
        if request.method == 'POST':
            user_form = UserRegistrationForm(request.POST)
            if user_form.is_valid():
                role = request.POST.get('user_role')
                if role == 'admin':
                    user = user_form.save()
                    assign_role(user, 'admin')
                    return redirect('shop:all_accounts')
                elif role == 'stuff':
                    user = user_form.save()
                    assign_role(user, 'stuff')
                    return redirect('shop:all_accounts')
            else:
                return render(request, 'shop/account/add_user.html')
        else:
            user_form = UserRegistrationForm()
        context = {
            'user_form': user_form,
        }
        return render(request, 'shop/account/add_user.html', context)
    else:
        return render(request, 'shop/account/permission_required.html')

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(
                user_form.cleaned_data['password'])
            new_user.save()
            auth_user = authenticate(username=user_form.cleaned_data['username'],
                                     password=user_form.cleaned_data['password'])
            if auth_user is not None:
                login(request, auth_user)
            return redirect('account:dashboard')
        else:
            return render(request, 'shop/account/register.html', {'user_form': user_form})

    else:
        user_form = UserRegistrationForm()
        return render(request, 'shop/account/register.html', {'user_form': user_form})


class AccountListView(ListView):
    model = User
    template_name = 'shop/account/accounts_list.html'
    context_object_name = 'accounts'


@login_required(login_url="/account/signin/")
def create_category(request):
    form=CategoryAddForm(request.POST or None)
    category=Category.objects.all()
    if form.is_valid():
        form.save()
        form = CategoryAddForm()
    else:
        form = CategoryAddForm()
    return render(request,
                  'shop/product/add_category.html',
                  {'form':form})

@login_required(login_url="/account/signin/")
def create_product(request):
    form=ProductAddForm(request.POST or None)
    products=Product.objects.all()
    if form.is_valid():
        form.save()
        form = ProductAddForm()
    else:
        form = ProductAddForm()
    return render(request,
                  'shop/product/add_product.html',
                  {'form':form,'product_list':products})


# def create_product(request):
#     data = dict()
#     if request.method == "GET":
#         categories_lists = Category.objects.all()
#         return render(request, 'shop/product/add_product.html', {"categories": categories_lists})
#     else:
#         # print(request.FILES)
#         Product.objects.create(
#             code=request.POST.get("code"),
#             category=Category.objects.get(id=request.POST.get("category")),
#             libelle=request.POST.get("libelle"),
#             slug=request.POST.get('slug'),
#             unite=request.POST.get('unite'),
#             quantite=request.POST.get("quantite"),
#             prix=request.POST.get("prix"),
#             cout_de_revient=request.POST.get("cout_de_revient"),
#
#         )
#         products_lists = Product.objects.all()
#     return render(request,'shop/product/add_product.html', {"products": products_lists})
    # return JsonResponse(data)
# @login_required(login_url="/account/signin/")
def products_ListView(request):
    template='shop/product/tables_products.html'
    products_lists = Product.objects.all()
    paginator = Paginator(products_lists, 10)
    page_number = request.GET.get('page')
    context = {"products": products_lists}
    try:
        prod_list = paginator.get_page(page_number)
    except PageNotAnInteger:
        prod_list = paginator.page(1)
    except EmptyPage:
        prod_list = paginator.page(paginator.num_pages)
    return render(request,template, {"products": products_lists,"prod_list":prod_list})

# @login_required(login_url="/account/signin/")
def ProductUpdateView(request, pk=None):
    product=get_object_or_404(Product, pk=pk)
    form=ProductAddForm(request.POST or None, instance=product)
    if form.is_valid():
        product=form.save(commit=False)
        product.save()
        messages.success(request, 'Vous avez modifié avec succès les paramètres de ce produit ')
        return redirect(reverse('shop:products_List'))
    else:
        form=ProductAddForm(instance=product)
    context={
            'code':product.code,
            'libelle':product.libelle,
            'slug':product.slug,
            'quantite':product.quantite,
            'prix':product.prix,
            'unite':product.unite,
            'cout_de_revient':product.cout_de_revient,
            'form':form,
            'instance':product
            }
    return render(request, 'shop/product/add_product.html', context)


@login_required(login_url="/account/signin/")
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(categorie=category)
    return render(request,
                  'shop/product/list.html',
                  {'category': category,
                   'categories': categories,
                   'products': products})


@login_required(login_url="/account/signin/")
def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()
    return render(request,
                  'shop/product/detail.html',
                  {'product': product,
                   'cart_product_form': cart_product_form})

@login_required(login_url="/account/signin/")
def CategorieList(request):
    CategorieList = Category.objects.all()
    return render(request,
                  'shop/product/ListCategorie.html',
                  {'CategorieList':CategorieList})
@login_required(login_url="/account/signin/")
def CategoryUpdateView(request, pk=None):
    category=get_object_or_404(Category, pk=pk)
    form=CategoryAddForm(request.POST or None, instance=category)
    if form.is_valid():
        product=form.save(commit=False)
        product.save()
        messages.success(request, 'Vous avez modifié avec succès les paramètres de cette catégorie ')
        return redirect(reverse('shop:listeCategory'))
    else:
        form=CategoryAddForm(instance=category)
    context={
            'nom':category.nom,
            'slug':category.slug,
            'form':form,
            'instance':category
            }
    return render(request, 'shop/product/add_category.html', context)

def signup(request):
    if request.method == "POST":
        if request.POST.get("pwd1") == request.POST.get("pwd2"):
            print(request.POST.get("pwd1"))
            user = User.objects.create(
                username=request.POST.get("username")
			)
            user.set_password(request.POST.get("pwd1"))
            user.save()
            return redirect("/account/signin/")
        else:
            return redirect("/account/signup/")
    return render(request, "shop/account/signup.html", {})


def signin(request):
    if request.method == "POST":
        pass
        user = authenticate(request, username=request.POST.get("username"), password=request.POST.get("password"))
        if user:
            login(request, user)
            return redirect("/")
        else:
            messages.error(request, "Erreur de nom d'utilisateur ou de mot de passe!")
            return redirect("/account/signin/")
    return render(request, "shop/account/login.html", {})


def logout_view(request):
	logout(request)
	return redirect("/account/signin/")