from django.shortcuts import render,redirect
from . models import *
from django.contrib import messages
from shop.form import CustomUserForm
from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    products=Product.objects.filter(trending=1)
    return render(request,"shop/index.html",{'products':products})


def login_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method=="POST":
            name=request.POST.get("username1")
            pwd=request.POST.get("password1")
            user=authenticate(request,username=name,password=pwd)
            if user is not None:
                login(request,user)
                messages.success(request,"login successfully")
                return redirect('/')
            else:
                messages.error(request,"invalid username or password")
                return redirect('/login')

        return render(request,"shop/login.html")

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logged out successfully")
    return redirect('/')

def register(request):
    form=CustomUserForm()
    if  request.method=='POST':
          form=CustomUserForm(request.POST)
          if form.is_valid():
              form.save()
              messages.success(request,"Registration success you can login now") 
              return redirect('/login')      
    return render(request,"shop/register.html",{'form':form})

def collections(request):
    catagory=Catagory.objects.filter(status=0)
    return render(request,'shop/collections.html',{"catagory":catagory})

def collectionsview(request,name):
    if(Catagory.objects.filter(status=0,name=name)):
        products=Product.objects.filter(category__name=name)
        return render(request,'shop/products/index.html',{"products":products,"category_name":name})
    else:
        messages.warning(request,'no such category found')
        return redirect('collections')
    

def product_details(request,cname,pname):
    if(Catagory.objects.filter(name=cname,status=0)):
      if(Product.objects.filter(name=pname,status=0)):
        products=Product.objects.filter(name=pname,status=0).first()
        return render(request,"shop/product_details.html",{"products":products})
      else:
        messages.error(request,"No Such Produtct Found")
        return redirect('collections')
    else:
      messages.error(request,"No Such Catagory Found")
      return redirect('collections')
    
def add_to_cart(request):
  if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_qty=data['product_qty']
      product_id=data['pid']
      # print(request.user.id)
      product_status=Product.objects.get(id=product_id)
      if product_status:
         if Cart.objects.filter(user=request.user.id,product_id=product_id):
             return JsonResponse({'status':'already in cart'},status=200)
         else:
            if product_status.quantity>=product_qty:
               Cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
               return JsonResponse({'status':'product add to cart now'},status=200)
            else:
               return JsonResponse({'status':'not available'},status=200)
    
    else:
      return JsonResponse({'status':'Login to add to cart'},status=200)
  else:
    return JsonResponse({'status':'Invalid Access'},status=200)


def cart_page(request):
   if request.user.is_authenticated:
      cart=Cart.objects.filter(user=request.user.id)
      return render(request,'shop/cart.html',{"cart":cart})
      
   else:
      return redirect('/')
   
def remove_cart(request,cid):
   cart_items=Cart.objects.get(id=cid)
   cart_items.delete()
   return redirect('/cart')

def fav_page(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Handle AJAX request
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # AJAX Request
            data = json.load(request)
            product_id = data['pid']
            product_status = Product.objects.get(id=product_id)
            if product_status:
                if Favourite.objects.filter(user=request.user.id, product_id=product_id):
                    return JsonResponse({'status': 'Product Already in Favourite'}, status=200)
                else:
                    Favourite.objects.create(user=request.user, product_id=product_id)
                    return JsonResponse({'status': 'Product Added to Favourite'}, status=200)
        else:  # Normal Request (Page Load)
            fav = Favourite.objects.filter(user=request.user)
            return render(request, "shop/fav.html", {"fav": fav})
    else:
        return JsonResponse({'status': 'Login to Add Favourite'}, status=200)

   

 
def favviewpage(request):
    if request.user.is_authenticated:
        fav = Favourite.objects.filter(user=request.user)
        return render(request, "shop/fav.html", {"fav": fav})
    else:
        return redirect("/")

 
def remove_fav(request,fid):
  item=Favourite.objects.get(id=fid)
  item.delete()
  return redirect("/favviewpage")