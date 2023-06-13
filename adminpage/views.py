from django.shortcuts import render, redirect
from django.contrib import messages
from .models import admindetails
from centers.models import centersdb, entries
from user.models import UserSignIn, message
from functools import wraps
from datetime import datetime, time, date, timedelta
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
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

def get_cookie(request):
    return request.COOKIES.get('admincookie')

def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        usercookie = request.COOKIES.get('admincookie')
        if usercookie:
            return view_func(request, *args, **kwargs)
        else:
            return redirect(adminsignin)
    return wrapper

def sendemail(sub, body, recipient):
    send_mail(
        sub,
        body,
        "201501002@rajalaskhmi.edu.com",
        [recipient]
    )

@login_required
def adminhome(request):
    user = admindetails.objects.get(cookiekey=get_cookie(request))
    context = {'name':user.username, 'rows':centersdb.objects.all()}
    if request.GET.get('search'):
        query = request.GET.get('search')
        rows = centersdb.objects.filter(id=query)
        context['rows'] = rows
        messages.info(request, 'Your search results for "'+query+'"')
        
    if request.GET.get('id'):
        id = request.GET.get('id')
        return HttpResponseRedirect('entriesof?id='+id)
    
    if request.method == 'POST':
        if request.POST.get('remove'):
            id = request.POST.get('remove')
            c = centersdb.objects.get(id=id)
            users = entries.objects.filter(centerid=c).values('userno').distinct()
            for user in users:
                row = UserSignIn.objects.get(mobileno=user['userno'])
                sub = "Regarding the centre you have booked"
                body = "Greetings "+row.name+",\n\tSorry for the inconvinience, the centre you have booked with ID: "+id+" with Name: "+c.name+" removed. Please book other centre.\n\t\t\t\tThank You\nBest Regard,\nCVB Team"
                recipient = row.email
                sendemail(sub, body, recipient)
                a = message.objects.create(
                    users = row,
                    sub=sub,
                    message=body
                )
                a.save()
            c.delete()
            messages.info(request, "Deleted Center Successfully of ID:"+id)     
            return redirect(adminhome)
            
            
    return render(request, 'base/adminhome.html', context)
    

def adminsignin(request):
    if get_cookie(request):
        try:
            user = admindetails.objects.get(cookiekey=get_cookie(request))
            return redirect('adminhome')
        except:
            return render(request, 'base/adminsignin.html')
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
            
    return render(request, 'base/adminsignin.html')


def adminlogout(request):
    response = HttpResponseRedirect('adminsignin')
    try:
        response.delete_cookie('admincookie')
    except:
        return response
    return response

@login_required
def adminadd(request):
    if request.GET.get('name'):
        name = request.GET.get('name')
        mobileno = request.GET.get('mobileno')
        line1 = request.GET.get('line1')
        line2 = request.GET.get('line2')
        city = request.GET.get('city')
        pincode = request.GET.get('pincode')
        dosage = request.GET.get('dosage')
        vacancy = request.GET.get('vacancy')
        slots = request.GET.get('slots')
        whfrom = request.GET.get('whfrom')
        whto = request.GET.get('whto')
        
        # return HttpResponse([name, mobileno, line1, line2, city, pincode, dosage, vacancy, slots, whfrom, whto])
        
        try:
            c = centersdb.objects.create(
                name=name,
                mobileno=mobileno,
                line1 = line1,
                line2 = line2,
                city = city,
                pincode = pincode,
                dosage = dosage,
                vacancy = vacancy,
                slots = slots,
                whfrom = whfrom,
                whto = whto,
                )
            c.save()
            messages.info(request, 'Successfully created')
        except Exception as e:
            messages.error(request, e)
        return redirect('adminhome')
    return render(request, 'base/adminadd.html')
    
@login_required    
def entriesof(request):
    if request.GET.get('id'):
        id = request.GET.get('id')
        idname = centersdb.objects.get(id=id) 
        rows = entries.objects.filter(centerid=id).order_by('entrydate')
        context = {'id':idname.id, 'name':idname.name, 'rows':rows}
    return render(request, 'base/entriesof.html', context)

@login_required
def modify(request, id):
    row = centersdb.objects.get(id=id)
    context = {'row':row}
    
    return render(request, 'base/modify.html', context)