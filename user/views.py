from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from .models import UserSignIn
from centers.models import entries, centersdb
from centers.views import matchingrows, mybookingsfilter, slots, futurebookingfilter, allbookingfilter
import base64
import hashlib
from datetime import datetime, time, date, timedelta
from django.db.models import Q

def index(request):
    return render(request, 'index.html')

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
    return request.COOKIES.get('usercookie')

def book(request, id):
    if get_cookie(request):
        try:
            row = centersdb.objects.get(id=id)
        except:
            return HttpResponse("The ID doesn't exist")
        
        if row.dosage < 1:
            messages.error(request, "There is no vaccine for the selected centre")
            return redirect(userhome)
        
        details = []
        for i in range(7):
            d = date.today() + timedelta(days=i)
            v = row.vacancy-entries.objects.filter(centerid=id, entrydate=d).count() if row.dosage>=row.vacancy else row.dosage
            s = slots(id, d)
            if v>0:
                details.append({'date':d, 'vacancy':v, 'slots':s})
        # return HttpResponse(slots(id))
        context = {'row':row, 'vacancy':row.dosage-entries.objects.filter(centerid=id).count(), 'details':details}
        userid = UserSignIn.objects.get(cookiekey=get_cookie(request))
        
        if request.GET.get('slot'):
            slot = request.GET.get('slot')
            datee = datetime.strptime(request.GET.get('date'), "%B %d, %Y").strftime("%Y-%m-%d")
            c = entries.objects.create(
                userno = userid,
                centerid = row,
                slot = slot,
                entrydate = datee
            )
            c.save()
            row.dosage-=1
            row.save()
            messages.success(request, "Booked the centre "+row.name+" with ID "+str(row.id)+" at "+datee+" of slot "+str(slot)+" successfully.")
        # else:
        #     messages.error(request, 'the slot is unavailable')
            return redirect(userhome)
        return render(request,'base/book.html', context)
    return render(request, usersignin)

def userhome(request):
    if get_cookie(request):
        userno = UserSignIn.objects.get(cookiekey=get_cookie(request))
        rows = centersdb.objects.all()
        context = {'name':userno.name, 'rows':rows}
        if request.GET.get('search'):
            query = request.GET.get('search')
            rows = matchingrows(query)
            # return HttpResponse(rows)
            context['rows']=rows
            if query!='':
                messages.info(request, 'Your search results for "'+query+'"')
            
        return render(request, 'base/userhome.html', context)
    return render(request, 'base/usersignin.html')
    

def usersignin(request):
    if get_cookie(request):
        try:
            user = UserSignIn.objects.get(cookiekey=get_cookie(request))
            return redirect('userhome')
        except:
            return render(request, 'base/usersignin.html')
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
            
    return render(request, 'base/usersignin.html')

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
        email = request.POST.get('email')
        password = request.POST.get('password')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        bloodgroup = request.POST.get('bloodgroup')
        # doorno = request.POST.get('doorno')
        # line1 = request.POST.get('line1')
        # line2 = request.POST.get('line2')
        # city = request.POST.get('city')
        # pincode = request.POST.get('pincode')
        try:
            c = UserSignIn.objects.create(
                name=name,
                mobileno=mobileno,
                email = email,
                password = hash_password(password),
                age = age,
                gender = gender,
                bloodgroup = bloodgroup,
                # doorno = doorno,
                # line1 = line1,
                # line2 = line2,
                # city = city,
                # pincode = pincode
                )
            c.save()
            messages.info(request, 'Successfully created')
        except:
            messages.error(request, 'User already exist please login')
        return redirect('usersignin')
    return render(request, 'base/usersignup.html')

    
def bookings(request):
    if get_cookie(request):
        cookiekey = get_cookie(request)
        context = {'rows':mybookingsfilter(cookiekey)}
        if request.GET.get('filter'):
            filter = request.GET.get('filter')
            if filter=='1':
                context = {'rows':mybookingsfilter(cookiekey)}
            if filter=='2':
                context = {'rows':futurebookingfilter(cookiekey)}
            if filter=="3":
                context = {'rows':allbookingfilter(cookiekey)}
            return render(request, 'base/bookings.html', context)
        return render(request, 'base/bookings.html', context)
    else:
        return redirect(usersignin)
    

