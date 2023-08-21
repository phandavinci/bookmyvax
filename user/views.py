from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from .models import UserSignIn, message
from centers.models import entries, centersdb
from django.core.exceptions import ObjectDoesNotExist
from centers.views import matchingrows, mybookingsfilter, slots, futurebookingfilter, allbookingfilter, vaccinatedbookings, bookednotvaccinated, slot
from django.core.mail import send_mail, get_connection
import base64
import hashlib
from functools import wraps
from datetime import datetime, time, date, timedelta
from django.db.models import Q
import pyqrcode, png

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


def sendmessage(request, c, sub, body):
    a = message.objects.create(
        users = c.userno,
        message=body
    )
    a.save()
    body = "Hey "+c.userno.name+",\n\t"+body+"\n\t\t\t\tThank You\nBest Regards,\nCVB Team"
    recipient = c.userno.email
    connection = get_connection()
    try:
        send_mail(
            sub,
            body,
            "201501002@rajalaskhmi.edu.com",
            [recipient],
            connection=connection
        )
    except:
        messages.error(request, "Can't able to send email")


def usersignin(request):
    if get_cookie(request):
        try:
            user = UserSignIn.objects.get(cookiekey=get_cookie(request))
            return redirect(userhome)
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
        try:
            c = UserSignIn.objects.create(
                name=name,
                mobileno=mobileno,
                email = email,
                password = hash_password(password),
                age = age,
                gender = gender,
                bloodgroup = bloodgroup,
                )
            c.save()
            messages.info(request, 'Successfully created')
        except:
            messages.error(request, 'User already exist please login')
        return redirect(usersignin)
    return render(request, 'base/usersignup.html')


@login_required
def userhome(request):
    userno = UserSignIn.objects.get(cookiekey=get_cookie(request))
    rows = centersdb.objects.all()
    for row in rows:
        row.dosage -= entries.objects.filter(Q(centerid=row.id) & Q(entrydate__gte=date.today()) | Q(is_vaccinated=True)).count()
    unread_count = message.objects.filter(users=userno, is_read=False).count()
    context = {'name':userno.name, 'rows':rows, 'unread_count':unread_count}
    
    if request.GET.get('search'):
        query = request.GET.get('search')
        rows = matchingrows(query)
        context['rows']=rows
        if query!='':
            messages.info(request, 'Your search results for "'+query+'"')
        
    if request.method=='POST':
        try:
            myself = request.POST.get('myself')
            id = request.POST.get('id')
        except:
            messages.error(request, 'Error occured, Please try again')
            return redirect(userhome)

        if myself=='1':
            request.session['centreid'] = id
            request.session['name'] = userno.name
            request.session['mobileno'] = userno.mobileno
            request.session['age'] = userno.age
            request.session['gender'] = userno.gender
            request.session['bloodgroup'] = userno.bloodgroup
            return redirect(book)
        else:
            request.session['centreid'] = id
            request.session['name'] = request.POST.get('name')
            request.session['mobileno'] = request.POST.get('mobileno')
            request.session['age'] = request.POST.get('age')
            request.session['gender'] = request.POST.get('gender')
            request.session['bloodgroup'] = request.POST.get('bloodgroup')
            return redirect(book)
            
        
    return render(request, 'base/userhome.html', context)

@login_required    
def book(request):
    try:
        id = request.session.get('centreid')
        name = request.session.get('name')
        mobileno = request.session.get('mobileno')
        age = request.session.get('age')
        gender = request.session.get('gender')
        bloodgroup = request.session.get('bloodgroup')
    except:
        messages.error(request, "Can't able to fetch details. Try again.")
        return redirect(userhome)
    
    chk = entries.objects.filter(mobileno=mobileno)
    if chk.filter(is_vaccinated=True).count():
        messages.info(request, "You are already Vaccinated")
        return redirect(userhome)
    todaybooked = min(chk.filter(entrydate=date.today()).values())['entrydate'] if chk.filter(entrydate=date.today()).count() else 0
    if chk.filter(entrydate__gt=date.today()) or (todaybooked and datetime.combine(todaybooked, slot(chk.get(entrydate = todaybooked))['t'])>datetime.now()):
        messages.info(request, "You already booked a Vaccine")
        return redirect(userhome)
                
                
    try:
        row = centersdb.objects.get(id=id)
    except:
        messages.error(request, "The centre with ID: "+str(id)+" not exist.")
        return redirect(userhome)
    
    userno = UserSignIn.objects.get(cookiekey=get_cookie(request))
    
    if row.dosage < 1:
        messages.error(request, "There is no vaccine for the selected centre")
        return redirect(userhome)
    
    details = []
    for i in range(7):
        d = date.today() + timedelta(days=i)
        s = slots(id, d)    
        v = sum(d['rem'] for d in s) if row.dosage>=row.vacancy else row.dosage
        rem = 4-entries.objects.filter(userno=userno, entrydate = d).count()
        if v>0:
            details.append({'date':d, 'vacancy':v, 'slots':s, 'rem':rem})
            
    context = {'row':row, 'details':details}
    
    if request.GET.get('slot'):
        slott = request.GET.get('slot')
        datee = datetime.strptime(request.GET.get('date'), "%b. %d, %Y").strftime("%Y-%m-%d")
        entry = 4-entries.objects.filter(userno=userno, entrydate = datee).count()
        # generating qr code
        try:
            next_id = entries.objects.all().order_by("-id")[0].id
        except:
            next_id=1
        key = ''.join([str(ord(i)+1)+' ' for i in str(next_id)+str(mobileno)+str(row)+name+str(age)+str(slot)])
        pyqrcode.create(key).png('media/qr_codes/'+str(next_id)+str(mobileno)+'.png')
        if entry:
            c = entries.objects.create(
                userno = userno,
                centerid = row,
                name= name,
                mobileno = mobileno,
                age = age,
                gender = gender,
                bloodgroup = bloodgroup,
                slot = slott,
                qr_code = 'qr_codes/'+str(next_id)+str(mobileno)+'.png',
                entrydate = datee,
            )
            c.save()
            s = slot(entries.objects.get(id=c.id))
            sub = "Slot booked successfully"
            body = "You have booked the centre "+row.name+" with ID "+str(row.id)+" for "+datee+" of slot "+str(s['f'])+" - "+str(s['t'])+" successfully, for the user named "+ c.name+" with Mobile number "+c.mobileno
            sendmessage(request, entries.objects.get(id=c.id), sub, body)
            messages.success(request, body)
        else:
            messages.error(request, 'you have exceed the limit for the day '+ datee+ ' of centre '+ row.name + ' with id '+ str(row.id))
        try:
            request.session.pop('centreid', None)
            request.session.pop('name', None)
            request.session.pop('mobileno', None)
            request.session.pop('age', None)
            request.session.pop('gender', None)
            request.session.pop('bloodgroup', None)
        except:
            return redirect(userhome)    
        return redirect(userhome)
    
    context['unread_count'] = message.objects.filter(users=userno, is_read=False).count()
    return render(request,'base/book.html', context)
    

@login_required
def bookings(request):
    cookiekey = get_cookie(request)
    userno = UserSignIn.objects.get(cookiekey=get_cookie(request))
    unread_count = message.objects.filter(users=userno, is_read=False).count()
    context = {'rows':mybookingsfilter(cookiekey), 'unread_count':unread_count, 'filter':'1'}
    
    if request.GET.get('filter'):
        filter = request.GET.get('filter')
        context['filter'] = filter
        if filter=='1':
            context['rows'] = mybookingsfilter(cookiekey)
        if filter=='2':
            context['rows'] = futurebookingfilter(cookiekey)
        if filter=="3":
            context['rows'] = allbookingfilter(cookiekey)
        if filter=="4":
            context['rows'] = vaccinatedbookings(cookiekey)
        if filter=="5":
            context['rows'] = bookednotvaccinated(cookiekey)
            
    if request.GET.get('id'):
        id = request.GET.get('id')
        filter = request.GET.get('filter')
        try:
            c = entries.objects.get(id=id)
        except:
            messages.error(request, "There is no entry with ID: "+str(id))
            return render(request, 'base/bookings.html', context)
        
        if slot(c)['cancel'][0] == 0: 
            c.delete()
        else:
            messages.error(request, "You can't cancel the booking with ID: "+str(id)+", because it is expired or already vaccinated.")
            return render(request, 'base/bookings.html', context)
        
        sub = "Booked slot Cancelled"
        body = "you have cancelled booking with ID "+id+" successfully."
        sendmessage(request, c, sub, body)
        messages.info(request, body)
        return HttpResponseRedirect('bookings?filter='+filter)
    return render(request, 'base/bookings.html', context)
    

@login_required
def msg(request):
    userno = UserSignIn.objects.get(cookiekey=get_cookie(request))
    msgs = message.objects.filter(users=userno)
    
    for m in msgs:
        if m.entrydatetime.date() < (datetime.today()-timedelta(days=6)).date():
            m.delete()
            continue
        m.is_read = True
        m.save()
        
    if request.GET.get('all'):
        all = request.GET.get('all')
        if all=='1':
            temp=message.objects.filter(users=userno)
            temp.delete()
            messages.success(request, "All messages deleted successfully")
        else:
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
    userno = UserSignIn.objects.get(cookiekey=get_cookie(request))
    unread_count = message.objects.filter(users=userno, is_read=False).count()
    context = {'unread_count':unread_count}
    return render(request, "base/certificatespage.html", context)