
from django.shortcuts import redirect, render
from .models import Pizza, PizzaCategory, Cart, CartItem 
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login ,authenticate
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.decorators import user_passes_test

# Create your views here.
# def logout_required(function=None, logout_url=settings.LOGOUT_URL):
#     actual_decorator = user_passes_test(
#         lambda u: not u.is_authenticated,
#         login_url=logout_url
#     )
#     if function:
#         return actual_decorator(function)
#     return actual_decorator

from django.contrib import messages
from instamojo_wrapper import Instamojo
from django.conf import settings
api = Instamojo(api_key=settings.API_KEY,
                auth_token=settings.AUTH_TOKEN ,endpoint="https://test.instamojo.com/api/1.1/")

def home(request):
    pizza = Pizza.objects.all()
    data = {
        "pizza": pizza
    }
    return render(request, 'home.html', data)


def Login(request):
    if request.method == 'POST':
        try:
           username = request.POST.get('username')
           password = request.POST.get('password')
           email = request.POST.get('email')
           user_obj = User.objects.filter(username=username, email=email)
           if not user_obj.exists():
             messages.warning(request, 'Your username not found.')
             return redirect('/login/')

           user_obj = authenticate(username=username ,password=password, email=email)
           if user_obj:
               login(request,user_obj)
               return redirect('/')
           messages.error(request, 'wrong password')

           return redirect('/login/')

        except Exception as e:
             messages.error(request, 'something went wrong.')
             return redirect('/login/')
    return render(request, 'Login.html')


def Register(request):
    if request.method=='POST':
        try:
           username = request.POST.get('username')
           password = request.POST.get('password')
           email = request.POST.get('email')
           user_obj = User.objects.filter(username=username, email=email)
           if user_obj.exists():
             messages.warning(request, 'Your username already taken.')
             return redirect('/register/')

           user_obj = User.objects.create(username=username, email=email)
           user_obj.set_password(password)
           user_obj.save()
           messages.success(request, 'Account created.')

           return redirect('/login/')

        except Exception as e:
             print(e)
             messages.error(request, 'something went wrong.')
             return redirect('/register/')
    return render(request, 'Register.html')

@login_required(login_url='/login/')
def add_cart(request ,pizza_uid):
      user =request.user
      pizza_obj = Pizza.objects.get(uid = pizza_uid)
      cart, _ = Cart.objects.get_or_create(user=user ,is_paid=False)
      CartItems =CartItem.objects.get_or_create(
           cart = cart,
           pizza = pizza_obj
      )
      return redirect('/')


@login_required(login_url='/login/')
def cart(request):
    carts =Cart.objects.get(is_paid =False ,user =request.user)
    response = api.payment_request_create(

        amount= carts.get_sum_total(),
        purpose='order',
        buyer_name=request.user.username,
        email="hassamafridi14@gmail.com",
        redirect_url="http://127.0.0.1:7000/success/",
    ) 
    carts.instamoji_id = response['payment_request']['id']
    carts.save()
    context={
        'cart':carts,
        'payment_url': response['payment_request']['longurl']
    }
    print(response )
    return render(request,'cart.html',context )


@login_required(login_url='/login/')
def remove_cart_items(request,cart_items_uid):
    try:
       CartItem.objects.get(uid =cart_items_uid).delete()
       return redirect('/cart/')
    except Exception as e:
        print(e)

def orders(request):
    order = Cart.objects.filter(is_paid = False, user= request.user)
    context ={
        'orders':order
    }
    return render(request ,'orders.html',context)

@login_required(login_url='/login/')
def success(request):
    payment_request = request.GET.get('payment_request_id')
    cart =Cart.objects.get(instamoji_id =payment_request)
    cart.save()
    return redirect('/order/')