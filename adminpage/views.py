from django.shortcuts import render, redirect
from django.contrib import messages
from .models import admindetails
from centers.models import centersdb, entries

from datetime import datetime, time, date, timedelta
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

def get_cookie(request):
    return request.COOKIES.get('admincookie')

def adminhome(request):
    if get_cookie(request):
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
            id = request.POST.get('remove')
            c = centersdb.objects.get(id=id)
            c.delete()
            messages.info(request, "Deleted Center Successfully of ID:"+id)
            return redirect(adminhome)
        return render(request, 'base/adminhome.html', context)
    return render(request, 'base/adminsignin.html')
    

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

def adminadd(request):
    
    if get_cookie(request):
        if request.GET.get('name'):
            name = request.GET.get('name')
            mobileno = request.GET.get('mobileno')
            line1 = request.GET.get('line1')
            line2 = request.GET.get('line2')
            city = request.GET.get('city')
            pincode = request.GET.get('pincode')
            whfrom = request.GET.get('whfrom')
            whto = request.GET.get('whto')
            wt = datetime.strptime(whto, '%H:%M').time()
            wf = datetime.strptime(whfrom, '%H:%M').time()
            t = datetime.combine(datetime.today(), wt)
            f = datetime.combine(datetime.today(), wf)
            total = abs((t - f)/3)
            slot1 = (f+total).time()
            slot2 = (f+(2*total)).time()
            
            #return HttpResponse([name, mobileno, line1, line2, city, pincode, whfrom, whto])
            
            try:
                c = centersdb.objects.create(
                    name=name,
                    mobileno=mobileno,
                    line1 = line1,
                    line2 = line2,
                    city = city,
                    pincode = pincode,
                    whfrom = whfrom,
                    whto = whto, 
                    slot1 = slot1,
                    slot2 = slot2
                    )
                c.save()
                messages.info(request, 'Successfully created')
            except Exception as e:
                messages.error(request, 'Sorry Unexpected Error Happened, Please Retry')
            return redirect('adminhome')
        return render(request, 'base/adminadd.html')
    return render(request, 'base/adminsignin.html')
    
def entriesof(request):
    if get_cookie(request):
        if request.GET.get('id'):
            id = request.GET.get('id')
            idname = centersdb.objects.get(id=id) 
            rows = entries.objects.filter(centerid=id).order_by('entrydate')
            context = {'id':idname.id, 'name':idname.name, 'rows':rows}
        return render(request, 'base/entriesof.html', context)
    return render(request, 'base/adminsignin.html')