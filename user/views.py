from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from .models import UserSignIn
from centers.models import entries, centersdb
from centers.views import matchingrows
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



def userhome(request):
    cookie = request.COOKIES.get('usercookie')
    if cookie:
        userno = UserSignIn.objects.get(cookiekey=cookie)
        context = {'name':userno.name}
        if request.method == 'POST':
            query = request.POST.get('search')
            rows = matchingrows(query)
            context['rows']=rows
            if query!='':
                messages.info(request, 'Your search results for "'+query+'"')
        
        if request.GET.get('book'):
            id = request.GET.get('book')
            name = centersdb.objects.get(id=id)
            c = entries.objects.create(
                centerid=name,
                userno = userno
            )
            c.save()
            messages.info(request, "You successfully booked for vaccination at '"+name.name+"'"+'  ID:'+id)
        return render(request, 'User/userhome.html', context)
    return render(request, 'User/usersignin.html')
    

def usersignin(request):
    cookie = request.COOKIES.get('usercookie')
    if cookie:
        try:
            user = UserSignIn.objects.get(cookiekey=cookie)
            return redirect('userhome')
        except:
            return render(request, 'User/usersignin.html')
    if request.method == 'POST':
        mobileno = request.POST.get('mobileno')
        password = request.POST.get('password')
        #return HttpResponse(hash_password(password))
        try:
            user = UserSignIn.objects.get(mobileno=mobileno, password=hash_password(password))
            response = HttpResponseRedirect("userhome")
            response.set_cookie(key='usercookie', value=generate_cookie_value(mobileno+password), path='/')
            user.cookiekey = generate_cookie_value(mobileno+password)
            user.save()
            return response
        except:
            messages.error(request, "Username or password is incorrect")
            
    return render(request, 'User/usersignin.html')

def userlogout(request):
    response = HttpResponseRedirect('usersignin')
    try:
        response.delete_cookie('usercookie')
    except:
        return response
    return response

def usersignup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        mobileno = request.POST.get('mobileno')
        password = request.POST.get('password')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        bloodgroup = request.POST.get('bloodgroup')
        doorno = request.POST.get('doorno')
        line1 = request.POST.get('line1')
        line2 = request.POST.get('line2')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        try:
            c = UserSignIn.objects.create(
                name=name,
                mobileno=mobileno,
                password = hash_password(password),
                age = age,
                gender = gender,
                bloodgroup = bloodgroup,
                doorno = doorno,
                line1 = line1,
                line2 = line2,
                city = city,
                pincode = pincode
                )
            c.save()
            messages.info(request, 'Successfully created')
        except:
            messages.error(request, 'User already exist please login')
        return redirect('usersignin')
    return render(request, 'User/usersignup.html')
    
def book(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        name = request.GET.get('name')
        try:
            cookie = request.COOKIES.get('usercookie')
            userno = UserSignIn.objects.get(cookie)
        except:
            return redirect(usersignin)
        c = entries.objects.create(
            centerid=id,
            userno = userno.mobileno
        )
        c.save()
        messages.info("You successfully booked for vaccination at"+name+'ID:'+id)
        return redirect(userhome)