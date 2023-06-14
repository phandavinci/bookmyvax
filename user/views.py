from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from .models import UserSignIn, message
from centers.models import entries, centersdb
from centers.views import matchingrows, mybookingsfilter, slots, futurebookingfilter, allbookingfilter, slot
import base64
import hashlib
from functools import wraps
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


def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        usercookie = request.COOKIES.get('usercookie')
        if usercookie:
            return view_func(request, *args, **kwargs)
        else:
            return redirect(usersignin)
    return wrapper

def get_cookie(request):
    return request.COOKIES.get('usercookie')


@login_required
def userhome(request):
    userno = UserSignIn.objects.get(cookiekey=get_cookie(request))
    rows = centersdb.objects.all()
    unread_count = message.objects.filter(users=userno, is_read=False).count()
    context = {'name':userno.name, 'rows':rows, 'unread_count':unread_count}
    if request.GET.get('search'):
        query = request.GET.get('search')
        rows = matchingrows(query)
        # return HttpResponse(rows)
        context['rows']=rows
        if query!='':
            messages.info(request, 'Your search results for "'+query+'"')
        
    return render(request, 'base/userhome.html', context)
    

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

@login_required
def bookings(request):
    cookiekey = get_cookie(request)
    userno = UserSignIn.objects.get(cookiekey=get_cookie(request))
    unread_count = message.objects.filter(users=userno, is_read=False).count()
    context = {'rows':mybookingsfilter(cookiekey), 'unread_count':unread_count}
    if request.GET.get('filter'):
        filter = request.GET.get('filter')
        context['filter'] = filter
        # return HttpResponse(context['filter'])
        if filter=='1':
            context['rows'] = mybookingsfilter(cookiekey)
        if filter=='2':
            context['rows'] = futurebookingfilter(cookiekey)
        if filter=="3":
            context['rows'] = allbookingfilter(cookiekey)
    # print(mybookingsfilter(cookiekey))
    if request.GET.get('id'):
        id = request.GET.get('id')
        c = entries.objects.get(id=id)
        c.delete()
        c.centerid.dosage+=1
        c.centerid.save()
        messages.info(request, "The booking with ID "+id+" is successfully cancelled")
        return redirect(bookings)
    return render(request, 'base/bookings.html', context)
    
@login_required    
def book(request, id):
    try:
        row = centersdb.objects.get(id=id)
    except:
        return HttpResponse("The ID doesn't exist")
    cookiekey = get_cookie(request)
    userno = UserSignIn.objects.get(cookiekey=get_cookie(request))
    unread_count = message.objects.filter(users=userno, is_read=False).count()
    context = {'rows':mybookingsfilter(cookiekey), 'unread_count':unread_count}
    
    if row.dosage < 1:
        messages.error(request, "There is no vaccine for the selected centre")
        return redirect(userhome)
    
    details = []
    for i in range(7):
        d = date.today() + timedelta(days=i)
        s = slots(id, d)    
        # return HttpResponse(slots(id, d))
        # print(slots(id, d),'\n')
        v = sum(d['rem'] for d in s) if row.dosage>=row.vacancy else row.dosage
        if v>0:
            details.append({'date':d, 'vacancy':v, 'slots':s})
    #return HttpResponse(details[1])
    context = {'row':row, 'vacancy':row.dosage-entries.objects.filter(centerid=id).count(), 'details':details}
    userid = UserSignIn.objects.get(cookiekey=get_cookie(request))
    
    if request.GET.get('slot'):
        slot = request.GET.get('slot')
        datee = datetime.strptime(request.GET.get('date'), "%B %d, %Y").strftime("%Y-%m-%d")
        entry = 4-entries.objects.filter(userno=userid, entrydate = datee).count()
        if entry:
            c = entries.objects.create(
                userno = userid,
                centerid = row,
                slot = slot,
                entrydate = datee
            )
            c.save()
            row.dosage-=1
            row.save()
            messages.success(request, "Booked the centre "+row.name+" with ID "+str(row.id)+" at "+datee+" of slot "+str(int(slot)+1)+" successfully.")
        else:
            messages.error(request, 'you have exceed the limit for the day '+ datee+ ' of centre '+ row.name + ' with id '+ str(row.id))
        return redirect(userhome)
    return render(request,'base/book.html', context)

@login_required
def msg(request):
    user = UserSignIn.objects.get(cookiekey=get_cookie(request))
    msgs = message.objects.filter(users=user)
    for m in msgs:
        if m.entrydatetime.date() < (datetime.today()-timedelta(days=6)).date():
            m.delete()
            continue
        m.is_read = True
        m.save()
    if request.GET.getlist('id'):
        id = request.GET.getlist('id')
        for i in id:
            temp = message.objects.get(id=i)
            temp.delete()
        messages.success(request, "Selected messages deleted successfully")
        return redirect(msg)
    context = {'msgs':msgs.order_by('-entrydatetime')}
    return render(request, 'base/msg.html', context)

@login_required
def certificatespage(request):
    return render(request, "base/certificatespage.html")