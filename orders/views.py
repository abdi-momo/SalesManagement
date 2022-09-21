from django.shortcuts import render
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect
from .render import render_to_pdf
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from shop.models import Product
from django.contrib.auth.decorators import login_required
import datetime
from datetime import date
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Q


@login_required(login_url="/account/signin/")
def order_create(request):
    cart = Cart(request)
    form = OrderCreateForm(request.POST or None)
    received_amount = request.POST.get('montant_recu')

    if request.method == 'POST':
        if form.is_valid():
            # order = form.save()
            total_cost = 0
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.utilisateur = request.user
            order.save()
            for item in cart:
                article = Product.objects.filter(libelle=item['product'])
                # Verifer si le montant saisi est inférieur au montant à payer
                if float(received_amount) < cart.get_total_price_after_discount():
                    messages.error(request, "Le montant " + received_amount + " est inférieur au montant à payer")
                    return redirect('orders:order_create')
                # Validation de la commande
                else:
                    for product in article:
                        prod = product.libelle
                        qte=product.quantite
                        finalQte=qte-item['quantity']
                        product.quantite=finalQte
                        article.update(quantite=finalQte)
                        # Vérification de la quantité en stock :
                        if product.quantite <= 10:
                            messages.warning(request,
                                          "Le seuil en stock du produit " + product.libelle + " est "
                                          + str(product.quantite) + " veuillez en rajouter! ")
                        OrderItem.objects.create(order=order,
                                     product=item['product'],
                                     price=item['price'],
                                     tva=item['tax_rate'],
                                     quantity=item['quantity'])
            # clear the cart
            cart.clear()
            return render(request,
                            'orders/order/created.html',
                            {'order': order,'refund':received_amount, 'cart':cart})
    else:
        form = OrderCreateForm()
    return render(request,
                'orders/order/create.html',
                {'cart': cart, 'form': form,'refund':received_amount})


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request,
                  'admin/orders/order/detail.html',
                  {'order': order})


@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    utilisateur=request.user
    pdf = render_to_pdf('orders/order/pdf.html', {'order': order, 'user':utilisateur})
    if pdf:
        response= HttpResponse(pdf,content_type='application/pdf')
        response['Content-Disposition'] = 'filename=\
                "order_{}.pdf"'.format(order.id)
        return response
    else:
        return HttpResponse("Fichier n'existe pas")

@login_required(login_url='/account/signin')
def order_list(request):
    order_list= Order.objects.all().order_by('-date_creation')
    return render(request,
                  'orders/order/order_list.html',
                  {'order_list':order_list})

@login_required(login_url='/account/signin')
def order_detail(request, id):
    order = get_object_or_404(Order, id=id)
    return render(request,
                  'orders/order/detail.html',
                  {'order': order})


@login_required(login_url='/account/signin')
def order_pdf(request, id):
    order = get_object_or_404(Order, id=id)
    utilisateur=request.user
    pdf = render_to_pdf('orders/order/pdf.html', {'order': order, 'user':utilisateur})
    if pdf:
        response= HttpResponse(pdf,content_type='application/pdf')
        response['Content-Disposition'] = 'filename=\
                "order_{}.pdf"'.format(order.id)
        return response
    else:
        return HttpResponse("Fichier n'existe pas")


@login_required(login_url="/account/signin/")
def daily_report(request):
    template = 'shop/product/list.html'
    orders=Order.objects.filter(utilisateur_id=request.user.id , date_creation= date.today().strftime("%Y-%m-%d"))
    daily_orders=Order.objects.filter(date_creation= date.today().strftime("%Y-%m-%d"))
    total_amount=0
    daily_totalAmount=0
    for order in orders:
        if order.utilisateur:
            total_amount=total_amount + order.get_total_cost()
    for daily_order in daily_orders:
        if daily_order.date_creation:
            daily_totalAmount=daily_totalAmount+daily_order.get_total_cost()
    print(daily_totalAmount)
    return render(request,
                  template,{'totalAmountPerDay':total_amount, 'daily_Sales':daily_totalAmount})
@staff_member_required(login_url="/account/signin")
def most_saled_products(request):
    template = 'orders/order/reports.html'
    list_product = []
    totol_quantity=0
    all_ord_items = OrderItem.objects.all()
    for element in all_ord_items:
        totol_quantity=totol_quantity+element.quantity
    print(totol_quantity)
    items = OrderItem.objects.all().distinct().order_by('-quantity')[:10]


    return render(request,
                  template,
                  {'data':items,
                   'total_quantity':totol_quantity})

@staff_member_required(login_url="/account/signin")
def most_valued_order(request):
    somme_benefice=0
    template = 'orders/order/important_sold.html'
    product = Product.objects.filter(order_items__in=OrderItem.objects.all())
    produit=Product.objects.all()
    top_sold = product.distinct().order_by('-prix')[:10]
    print(top_sold)
    for item in top_sold:
        if item.pk:
            somme_benefice = somme_benefice + item.get_cost_margin()
    return render(request,
                  template,
                  {'top_sold':top_sold,
                   'benefice':somme_benefice
                   })

@staff_member_required(login_url="/account/signin")
def chart(request, pk=None):

    order_list=[i['quantity'] for i in OrderItem.objects.all().values('quantity')]
    # print(order_list)

    context={'order_list':order_list}
    return render(request,
                  'orders/order/chart.html',
                  context)


@staff_member_required(login_url="/account/signin")
def monthly_report(request):
    if request.method == 'GET':
        # from_date=datetime.datetime.strptime(request.GET.get('datedebut',None),'%Y-%m-%d')
        from_date = request.GET.get('datedebut', None)
        to_date = request.GET.get('datefin',None)
        utilisateur = request.GET.get('user', None)
        orderList=Order.objects.filter(Q(date_creation__range=(from_date,to_date))).order_by('-id')
        # print(orderList)
        #|Order.objects.filter(Q(utilisateur=utilisateur))
    return  render(request,
                   'orders/order/monthly_report.html', {'orderList':orderList})
