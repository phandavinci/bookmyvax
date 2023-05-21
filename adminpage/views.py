from django.shortcuts import render, redirect
from django.contrib import messages
from .models import admindetails
from centers.models import centersdb, entries
from django.http import HttpResponse, HttpResponseRedirect
import base64
import hashlib


def hash_password(password):
    secret_key = 'sidfht34985ty34q8h58934y54hsdfngshtgdsgfn45023'
    user_data = str(password)
    combined_data = secret_key + user_data
    encoded_value = base64.urlsafe_b64encode(hashlib.sha256(combined_data.encode()).digest())
    hashedpass = encoded_value.decode()
    return hashedpass


def generate_cookie_value(user_id):
    secret_key = 'hsdaifuhf34ry52938y982h93h892htfhfdjnfasdufh98whr'
    user_data = str(user_id)
    combined_data = secret_key + user_data
    encoded_value = base64.urlsafe_b64encode(hashlib.sha256(combined_data.encode()).digest())
    cookie_value = encoded_value.decode()
    return cookie_value



def adminhome(request):
    cookie = request.COOKIES.get('admincookie')
    if cookie:
        userno = admindetails.objects.get(cookiekey=cookie)
        if request.method == 'POST':
            query = request.POST.get('search')
            rows = 0
            rows = {'rows':rows}
            return render(request, 'Admin/adminhome.html', rows)
        
        if request.GET.get('book'):
            id = request.GET.get('book')
            name = centersdb.objects.get(id=id)
            c = entries.objects.create(
                centerid=name,
                userno = userno
            )
            c.save()
            messages.info(request, "You successfully booked for vaccination at"+name.name+'  ID:'+id)
        return render(request, 'Admin/adminhome.html', {"name":userno.username})
    return render(request, 'Admin/adminsignin.html')
    

def adminsignin(request):
    cookie = request.COOKIES.get('admincookie')
    if cookie:
        try:
            user = admindetails.objects.get(cookiekey=cookie)
            return redirect('adminhome')
        except:
            return render(request, 'Admin/adminsignin.html')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # return HttpResponse(hash_password(password))
        try:
            user = admindetails.objects.get(username=username, password=hash_password(password))
            response = HttpResponseRedirect("/adminhome")
            response.set_cookie(key='admincookie', value=generate_cookie_value(username+password), path='/')
            user.cookiekey = generate_cookie_value(username+password)
            user.save()
            return response
        except:
            messages.error(request, "Username or password is incorrect")
            
    return render(request, 'Admin/adminsignin.html')

def adminlogout(request):
    response = HttpResponseRedirect('adminsignin')
    try:
        response.delete_cookie('admincookie')
    except:
        return response
    return response

def adminadd(request):
    if request.GET.get('name'):
        name = request.GET.get('name')
        mobileno = request.GET.get('mobileno')
        line1 = request.GET.get('line1')
        line2 = request.GET.get('line2')
        city = request.GET.get('city')
        pincode = request.GET.get('pincode')
        whfrom = request.GET.get('whfrom')
        whto = request.GET.get('whto')
        return HttpResponse([name, mobileno, line1, line2, city, pincode, whfrom, whto])
        
        try:
            c = admindetails.objects.create(
                name=name,
                mobileno=mobileno,
                line1 = line1,
                line2 = line2,
                city = city,
                pincode = pincode,
                whfrom = whfrom,
                whto = whto
                )
            c.save()
            messages.info(request, 'Successfully created')
        except:
            messages.error(request, 'An error occured')
        return redirect('adminhome')
    return render(request, 'Admin/adminadd.html')
    