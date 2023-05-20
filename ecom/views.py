from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings

from .forms import CustomerUserForm, CustomerForm, ProductForm, OrderForm, FeedbackForm, AddressForm, ContactusForm, \
    CategoryForm, BrandForm
from .models import Product, Customer, Orders, Feedback, Category, Brand
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse


def home_view(request):
    products = Product.objects.all()
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0
    if request.user.is_authenticated:
        return HttpResponseRedirect('after_login')
    return render(request, 'ecom/index.html', {'products': products, 'product_count_in_cart': product_count_in_cart})


def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('after_login')
    return HttpResponseRedirect('admin_login')


def customer_signup_view(request):
    user_Form = CustomerUserForm()
    customer_Form = CustomerForm()
    mydict = {'userForm': user_Form, 'customerForm': customer_Form}
    if request.method == 'POST':
        userForm = CustomerUserForm(request.POST)
        customerForm = CustomerForm(request.POST, request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            customer = customerForm.save(commit=False)
            customer.user = user
            customer.save()
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)
        return HttpResponseRedirect('customer_login')
    return render(request, 'ecom/customer_signup.html', context=mydict)


def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()


def after_login_view(request):
    if is_customer(request.user):
        return redirect('customer-home')
    else:
        return redirect('admin-dashboard')


@login_required(login_url='admin_login')
def admin_dashboard_view(request):
    customercount = Customer.objects.all().count()
    productcount = Product.objects.all().count()
    ordercount = Orders.objects.all().count()

    orders = Orders.objects.all()
    ordered_products = []
    ordered_bys = []
    for order in orders:
        ordered_product = Product.objects.all().filter(id=order.product.id)
        ordered_by = Customer.objects.all().filter(id=order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)
    mydict = {
        'customercount': customercount,
        'productcount': productcount,
        'ordercount': ordercount,
        'data': zip(ordered_products, ordered_bys, orders),
    }
    return render(request, 'ecom/admin_dashboard.html', context=mydict)


@login_required(login_url='admin_login')
def view_customer_view(request):
    customers = Customer.objects.all()
    return render(request, 'ecom/view_customer.html', {'customers': customers})


# admin delete customer
@login_required(login_url='admin_login')
def delete_customer_view(request, pk):
    customer = Customer.objects.get(id=pk)
    user = User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect('view-customer')


@login_required(login_url='admin_login')
def update_customer_view(request, pk):
    customer = Customer.objects.get(id=pk)
    user = User.objects.get(id=customer.user_id)
    userForm = CustomerUserForm(instance=user)
    customerForm = CustomerForm(request.FILES, instance=customer)
    mydict = {'userForm': userForm, 'customerForm': customerForm}
    if request.method == 'POST':
        userForm = CustomerUserForm(request.POST, instance=user)
        customerForm = CustomerForm(request.POST, instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('view-customer')
    return render(request, 'ecom/admin_update_customer.html', context=mydict)


@login_required(login_url='admin_login')
def admin_products_view(request):
    products = Product.objects.all()
    return render(request, 'ecom/admin_products.html', {'products': products})


# admin add product by clicking on floating button
@login_required(login_url='admin_login')
def admin_add_product_view(request):
    productForm = ProductForm()
    if request.method == 'POST':
        productForm = ProductForm(request.POST, request.FILES)
        if productForm.is_valid():
            productForm.save()
        return HttpResponseRedirect('admin-products')
    return render(request, 'ecom/admin_add_products.html', {'productForm': productForm})


@login_required(login_url='admin_login')
def delete_product_view(request, pk):
    product = Product.objects.get(id=pk)
    product.delete()
    return redirect('admin-products')


@login_required(login_url='admin_login')
def update_product_view(request, pk):
    product = Product.objects.get(id=pk)
    productForm = ProductForm(instance=product)
    if request.method == 'POST':
        productForm = ProductForm(request.POST, request.FILES, instance=product)
        if productForm.is_valid():
            productForm.save()
            return redirect('admin-products')
    return render(request, 'ecom/admin_update_product.html', {'productForm': productForm})


@login_required(login_url='admin_login')
def admin_view_booking_view(request):
    orders = Orders.objects.all()
    ordered_products = []
    ordered_bys = []
    for order in orders:
        ordered_product = Product.objects.all().filter(id=order.product.id)
        ordered_by = Customer.objects.all().filter(id=order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)
    return render(request, 'ecom/admin_view_booking.html', {'data': zip(ordered_products, ordered_bys, orders)})


@login_required(login_url='admin_login')
def delete_order_view(request, pk):
    order = Orders.objects.get(id=pk)
    order.delete()
    return redirect('admin-view-booking')


@login_required(login_url='admin_login')
def update_order_view(request, pk):
    order = Orders.objects.get(id=pk)
    orderForm = OrderForm(instance=order)
    if request.method == 'POST':
        orderForm = OrderForm(request.POST, instance=order)
        if orderForm.is_valid():
            orderForm.save()
            return redirect('admin-view-booking')
    return render(request, 'ecom/update_order.html', {'orderForm': orderForm})


@login_required(login_url='admin_login')
def view_feedback_view(request):
    feedbacks = Feedback.objects.all().order_by('-id')
    return render(request, 'ecom/view_feedback.html', {'feedbacks': feedbacks})


def search_view(request):
    query = request.GET['query']
    products = Product.objects.all().filter(name__icontains=query)
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0

    word = "Searched Result :"

    if request.user.is_authenticated:
        return render(request, 'ecom/customer_home.html',
                      {'products': products, 'word': word, 'product_count_in_cart': product_count_in_cart})
    return render(request, 'ecom/index.html',
                  {'products': products, 'word': word, 'product_count_in_cart': product_count_in_cart})


def add_to_cart_view(request, pk):
    products = Product.objects.all()
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 1

    response = render(request, 'ecom/index.html',
                      {'products': products, 'product_count_in_cart': product_count_in_cart})

    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids == "":
            product_ids = str(pk)
        else:
            product_ids = product_ids + "|" + str(pk)
        response.set_cookie('product_ids', product_ids)
    else:
        response.set_cookie('product_ids', pk)

    product = Product.objects.get(id=pk)
    messages.info(request, product.name + ' added to cart successfully!')

    return response


def cart_view(request):
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0

    products = None
    total = 0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart = product_ids.split('|')
            products = Product.objects.filter(id__in=product_id_in_cart)

            for p in products:
                total = total + p.price
    return render(request, 'ecom/cart.html',
                  {'products': products, 'total': total, 'product_count_in_cart': product_count_in_cart})


def remove_from_cart_view(request, pk):
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0

    total = 0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_id_in_cart = product_ids.split('|')
        product_id_in_cart = list(set(product_id_in_cart))
        product_id_in_cart.remove(str(pk))
        products = Product.objects.filter(id__in=product_id_in_cart)
        for p in products:
            total = total + p.price
        value = ""
        for i in range(len(product_id_in_cart)):
            if i == 0:
                value = value + product_id_in_cart[0]
            else:
                value = value + "|" + product_id_in_cart[i]
        response = render(request, 'ecom/cart.html',
                          {'products': products, 'total': total, 'product_count_in_cart': product_count_in_cart})
        if value == "":
            response.delete_cookie('product_ids')
        response.set_cookie('product_ids', value)
        return response


def send_feedback_view(request):
    feedbackForm = FeedbackForm()
    if request.method == 'POST':
        feedbackForm = FeedbackForm(request.POST)
        if feedbackForm.is_valid():
            feedbackForm.save()
            return render(request, 'ecom/feedback_sent.html')
    return render(request, 'ecom/feedback_sent.html', {'feedbackForm': feedbackForm})


@login_required(login_url='customer_login')
@user_passes_test(is_customer)
def customer_home_view(request):
    products = Product.objects.all()
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0
    return render(request, 'ecom/customer_home.html',
                  {'products': products, 'product_count_in_cart': product_count_in_cart})


@login_required(login_url='customer_login')
def customer_address_view(request):
    product_in_cart = False
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_in_cart = True
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0

    addressForm = AddressForm()
    if request.method == 'POST':
        addressForm = AddressForm(request.POST)
        if addressForm.is_valid():
            email = addressForm.cleaned_data['Email']
            mobile = addressForm.cleaned_data['Mobile']
            address = addressForm.cleaned_data['Address']
            total = 0
            if 'product_ids' in request.COOKIES:
                product_ids = request.COOKIES['product_ids']
                if product_ids != "":
                    product_id_in_cart = product_ids.split('|')
                    products = Product.objects.all().filter(id__in=product_id_in_cart)
                    for p in products:
                        total = total + p.price

            response = render(request, 'ecom/payment.html', {'total': total})
            response.set_cookie('email', email)
            response.set_cookie('mobile', mobile)
            response.set_cookie('address', address)
            return response
    return render(request, 'ecom/customer_address.html',
                  {'addressForm': addressForm, 'product_in_cart': product_in_cart,
                   'product_count_in_cart': product_count_in_cart})


@login_required(login_url='customer_login')
def payment_success_view(request):
    customer = Customer.objects.get(user_id=request.user.id)
    products = None
    email = None
    mobile = None
    address = None
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart = product_ids.split('|')
            products = Product.objects.all().filter(id__in=product_id_in_cart)
    if 'email' in request.COOKIES:
        email = request.COOKIES['email']
    if 'mobile' in request.COOKIES:
        mobile = request.COOKIES['mobile']
    if 'address' in request.COOKIES:
        address = request.COOKIES['address']
    for product in products:
        Orders.objects.get_or_create(customer=customer, product=product, status='Pending', email=email,
                                     mobile=mobile, address=address)

    response = render(request, 'ecom/payment_success.html')
    response.delete_cookie('product_ids')
    response.delete_cookie('email')
    response.delete_cookie('mobile')
    response.delete_cookie('address')
    return response


@login_required(login_url='customer_login')
@user_passes_test(is_customer)
def my_order_view(request):
    customer = Customer.objects.get(user_id=request.user.id)
    orders = Orders.objects.all().filter(customer_id=customer)
    ordered_products = []
    for order in orders:
        ordered_product = Product.objects.all().filter(id=order.product.id)
        ordered_products.append(ordered_product)

    return render(request, 'ecom/my_order.html', {'data': zip(ordered_products, orders)})


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return


@login_required(login_url='customer_login')
@user_passes_test(is_customer)
def download_invoice_view(request, orderID, productID):
    order = Orders.objects.get(id=orderID)
    product = Product.objects.get(id=productID)
    mydict = {
        'orderDate': order.order_date,
        'customerName': request.user,
        'customerEmail': order.email,
        'customerMobile': order.mobile,
        'shipmentAddress': order.address,
        'orderStatus': order.status,

        'productName': product.name,
        'productImage': product.product_image,
        'productPrice': product.price,
        'productDescription': product.description,

    }
    return render_to_pdf('ecom/download_invoice.html', mydict)


@login_required(login_url='customer_login')
@user_passes_test(is_customer)
def my_profile_view(request):
    customer = Customer.objects.get(user_id=request.user.id)
    return render(request, 'ecom/my_profile.html', {'customer': customer})


@login_required(login_url='customer_login')
@user_passes_test(is_customer)
def edit_profile_view(request):
    customer = Customer.objects.get(user_id=request.user.id)
    user = User.objects.get(id=customer.user_id)
    userForm = CustomerUserForm(instance=user)
    customerForm = CustomerForm(request.FILES, instance=customer)
    mydict = {'userForm': userForm, 'customerForm': customerForm}
    if request.method == 'POST':
        userForm = CustomerUserForm(request.POST, instance=user)
        customerForm = CustomerForm(request.POST, instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return HttpResponseRedirect('my-profile')
    return render(request, 'ecom/edit_profile.html', context=mydict)


def aboutus_view(request):
    return render(request, 'ecom/about_us.html')


def contactus_view(request):
    sub = ContactusForm()
    if request.method == 'POST':
        sub = ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name = sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name) + ' || ' + str(email), message, settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER,
                      fail_silently=False)
            return render(request, 'ecom/contactus_success.html')
    return render(request, 'ecom/contactus.html', {'form': sub})


def category_view(request):
    cat = CategoryForm()
    category = Category.objects.all()
    if request.method == 'POST':
        cat = CategoryForm(request.POST)
        if cat.is_valid():
            cat.save()
            return render(request, 'ecom/index.html', {'category': category})
    return render(request, 'ecom/index.html', {'form': cat})


def brand_view(request):
    bran = BrandForm()
    brand = Brand.objects.all()
    if request.method == 'POST':
        cat = BrandForm(request.POST)
        if cat.is_valid():
            cat.save()
            return render(request, 'ecom/index.html', {'brand': brand})
    return render(request, 'ecom/index.html', {'form': bran})
