from django.shortcuts import render, redirect
from django.contrib import messages
from .models import admindetails
from centers.views import slot, dosagecount
from centers.models import centersdb, entries
from user.models import UserSignIn, message
from functools import wraps
from datetime import datetime, time, date, timedelta
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
from django.db.models import Q
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

def sendmessage(request, c, dele, name='', words=[]):
    users = entries.objects.filter(centerid=c, entrydate__gte=date.today()).values('userno').distinct()
    for user in users:
        row = UserSignIn.objects.get(mobileno=user['userno'])
        if dele:
            sub = "Regarding the removal of centre that you booked"
            body = "Sorry for the inconvinience, the centre you have booked with ID: "+str(c.id)+" with Name: "+c.name+" removed for some technical reasons. Please book other centre."
        else:
            sub = "Regarding the changes in centre that you booked"
            body = "Due to some technical reasons, the CVB Team has did some changes in the centre with ID: "+str(c.id)+" and Name: "+name+" that you have booked, \n\n"+''.join(words)+"\nAlso, You received a message and can check those information in the bookings section in our website."
        a = message.objects.create(
            users = row,
            message=body
        )
        a.save()
        body = "Hey "+row.name+",\n\t"+body+"\n\t\t\t\tThank You\nBest Regards,\nCVB Team"
        recipient = row.email
        try:
            send_mail(
                sub,
                body,
                "201501002@rajalaskhmi.edu.com",
                [recipient]
            )
        except:
            messages.error(request, "Can't able to send email")


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
def adminhome(request):
    user = admindetails.objects.get(cookiekey=get_cookie(request))
    rows = centersdb.objects.all()
    for row in rows:
        row.dosage -= len(dosagecount(row))
    context = {'name':user.username, 'rows':rows}
    
    if request.GET.get('search'):
        query = request.GET.get('search')
        rows = centersdb.objects.filter(id=query)
        context['rows'] = rows
        messages.info(request, 'Your search results for "'+query+'"')
    
    if request.method == 'POST':
        if request.POST.get('remove'):
            id = request.POST.get('remove')
            c = centersdb.objects.get(id=id)
            sendmessage(request, c, 1)
            c.delete()
            messages.info(request, "Deleted Center Successfully of ID:"+id)     
            return redirect(adminhome)
            
            
    return render(request, 'base/adminhome.html', context)
    
@login_required    
def entriesof(request, id):
    
    def getslot(rows):
        for row in rows:
            row.slot = slot(row)
        return rows
    
    def esendmessage(request, c, sub, body):
        a = message.objects.create(
            users = c.userno,
            message=body
        )
        a.save()
        body = "Hey "+c.userno.name+",\n\t"+body+"\n\t\t\t\tThank You\nBest Regards,\nCVB Team"
        recipient = c.userno.email
        try:
            send_mail(
                sub,
                body,
                "201501002@rajalaskhmi.edu.com",
                [recipient]
            )   
        except:
            messages.error(request, "Can't able to send email") 
    try:    
        idname = centersdb.objects.get(id=id) 
        rows = entries.objects.filter(centerid=id).order_by('-entrydate')
        context = {'id':idname.id, 'name':idname.name, 'rows':getslot(rows)}
    except:
        messages.error(request, "There is no Centre with ID "+str(id))
        return redirect(adminhome)
            
    if request.GET.get('id'):
        ide = request.GET.get('id')
        try:
            c = entries.objects.get(id=ide)
        except:
            messages.error(request, "There is no entry with ID "+str(ide))
            return HttpResponseRedirect(id)
        c.delete()
        sub = "Booked slot Cancelled"
        body = "The Admin cancelled your booking with ID "+ide+" successfully."
        esendmessage(request, c, sub, body)
        messages.info(request, body)
        return HttpResponseRedirect(id)
    return render(request, 'base/entriesof.html', context)


@login_required
def modify(request, id):
    
    def modifyfunc(sec,t, f, words):
        words.append(sec+":\n"+"\t"+str(f)+" -> "+str(t)+"\n")
        return words
    try:
        row = centersdb.objects.get(id=id)
    except:
        messages.error(request, "There is no centre with the ID: "+id)
        return redirect(adminhome)
    
    context = {'row':row}
    flag =  dosage = 0
    words = []
    name = row.name
    
    if request.GET.get('name'):
        words =  modifyfunc('Name', request.GET.get('name'), row.name, words)
        row.name=request.GET.get('name')
    if request.GET.get('mobileno'):
        words =  modifyfunc('Mobile Number', request.GET.get('mobileno'), row.mobileno, words)
        row.mobileno = request.GET.get('mobileno')
    if request.GET.get('line1'):
        words =  modifyfunc('Address Line1', request.GET.get('line1'), row.line1, words)
        row.line1 = request.GET.get('line1')
    if request.GET.get('line2'):
        words =  modifyfunc('Address Line2', request.GET.get('line2'), row.line2, words)
        row.line2 = request.GET.get('line2')
    if request.GET.get('city'):
        words =  modifyfunc('City', request.GET.get('city'), row.city, words)
        row.city = request.GET.get('city')
    if request.GET.get('pincode'):
        words =  modifyfunc('Pincode', request.GET.get('pincode'), row.pincode, words)
        row.pincode = request.GET.get('pincode')
    if request.GET.get('dosage'):
        dosage = int(request.GET.get('dosage'))
        row.dosage+=dosage
    if request.GET.get('vacancy'):
        words =  modifyfunc('Vacancy', request.GET.get('vacancy'), row.vacancy, words)
        row.vacancy = request.GET.get('vacancy')
        flag = 1
    if request.GET.get('slots'):
        words =  modifyfunc('Slots', request.GET.get('slots'), row.slots, words)
        row.slots = request.GET.get('slots')
        flag = 1
    if request.GET.get('whfrom'):
        words =  modifyfunc('Woking Hours(from)', request.GET.get('whfrom'), row.whfrom, words)
        row.whfrom = request.GET.get('whfrom')
        flag = 1
    if request.GET.get('whto'):
        words =  modifyfunc('Working Hours(to)', request.GET.get('whto'), row.whto, words)
        row.whto = request.GET.get('whto')
        flag = 1
        
    
    if flag:
        words.append("\nDue to the change in slots, Your entries have deleted. Please select another slot for your convinience from the updated slots.\n ")
        
    if words or dosage:
        if words:
            sendmessage(request, row, 0, name, words)
            if flag:
                rows = entries.objects.filter(centerid=row)
                cnt = rows.count()
                row.dosage+=cnt
                rows.delete()
        row.save()
        messages.info(request, "Modified Center with ID "+str(id)+ "Successfully.")     
        return redirect(adminhome)
    
    return render(request, 'base/modify.html', context)



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
        except Exception:
            messages.error(request, "An unexpected error happened. Please try again.")
        return redirect('adminhome')
    return render(request, 'base/adminadd.html')
    



@login_required
def scanqr(request):
    return render(request, 'base/scanqr.html')