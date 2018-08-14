from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login,logout
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.db.models import Q

import json

from django.template import loader, Context
from django.views.decorators.http import require_http_methods

from .models import *



def home(request):
    return render(request, 'home.html')

@login_required(login_url='/login')
def examp(request):
    return render(request, 'examp.html')

@login_required(login_url='/login')
def dashboard(request):
    company = Company.objects.filter(user=request.user).first()
    if not company:
        return HttpResponse(status=500)

    computers = Computers.objects.filter(company=company)
    alert = Alerts.objects.filter(computer__company = company)[:10]
    return render(request, "logged.html", dict(name = "Shimi", computers=computers ,alerts=alert))




@login_required(login_url='/login')
def computer(request, computer_id):
    company = Company.objects.filter(user=request.user).first()
    computer = Computers.objects.get(id=computer_id, company=company)
    logs = Logs.objects.filter(computer=computer).order_by('-time_created')[:10]
    #alerts = Alerts.objects.filter(computer=computer)[:10]
    disk = Statistics.objects.filter(type ="disk").order_by('-time_created').first()
    disk_content = json.loads(disk.content)
    cpu = Statistics.objects.filter(type="cpu").order_by('-time_created').first()
    cpu_content= json.loads(cpu.content)
    virtual_memory=Statistics.objects.filter(type = "virtual memory").order_by('-time_created').first()
    memory_content = json.loads(virtual_memory.content)
    softwares = Software.objects.filter(computer=computer, upgrade_version__isnull=False)
    print("SOFTWARE\n\n", len(softwares))
    return render(request, "computer.html", dict(computer=computer,
                                                 gaga=logs,
                                                 alerts = alerts,
                                                 disk=disk_content,
                                                 cpu=cpu_content,
                                                 virtual_memory = memory_content,
                                                 softwares=softwares))

@login_required(login_url='/login')
@require_POST
def computer_install_update(request, computer_id, update_id):
    company = Company.objects.filter(user=request.user).first()
    computer = Computers.objects.get(id=computer_id, company=company)
    software = Software.objects.get(id=update_id, computer=computer)

    # If in progress, do nothing
    if computer.upgrade_in_progress:
        return redirect("computer", computer_id=computer_id)

    # Send command
    Command.objects.create(
        computer=computer,
        command="apt install -y --upgrade " + software.name,
        errors=False,
        sent=False,
        completed=False
    ).save()

    Command.objects.create(
        computer=computer,
        command="apt list --installed",
        errors=False,
        sent=False,
        completed=False
    ).save()

    # Mark computer as in progress
    computer.upgrade_in_progress = True
    computer.save()

    return redirect("computer", computer_id=computer_id)

@login_required(login_url='/login')
@require_GET
def computer_updates_in_progress(request, computer_id):
    company = Company.objects.filter(user=request.user).first()
    computer = Computers.objects.get(id=computer_id, company=company)

    return JsonResponse(dict(in_progress=computer.upgrade_in_progress))

@login_required(login_url='/login')
@require_POST
def computer_check_updates(request, computer_id):
    company = Company.objects.filter(user=request.user).first()
    computer = Computers.objects.get(id=computer_id, company=company)

    # If in progress, do nothing
    if computer.upgrade_in_progress:
        return redirect("computer", computer_id=computer_id)

    # Send command
    Command.objects.create(
        computer=computer,
        command="apt update",
        errors=False,
        sent=False,
        completed=False
    ).save()

    Command.objects.create(
        computer=computer,
        command="apt list --installed",
        errors=False,
        sent=False,
        completed=False
    ).save()

    # Mark computer as in progress
    computer.upgrade_in_progress = True
    computer.save()

    # Redirect to computer
    return redirect("computer", computer_id=computer_id)

@login_required(login_url='/login')
def alerts(request):
    company = Company.objects.filter(user=request.user).first()
    if not company:
        return HttpResponse(status=500)

    computers = Computers.objects.filter(company=company)
    alert = Alerts.objects.filter(computer__company = company).all()
    return render(request, "alerts.html",dict(name="Shimi", computers=computers ,alerts=alert))

@login_required(login_url='/login')
def approve_alert(request, alert_id):
    alert = Alerts.objects.get(id=alert_id)
    alert.read_by_user = True
    alert.save()

    return HttpResponse()

@login_required(login_url='/login')
@require_http_methods(['GET'])
def search(request):
    q = request.GET.get('q')
    alerts = Alerts.objects.filter(Q(severity_level__icontains=q)|
                                   Q(alert_description__icontains=q)).distinct()
    return render(request, "search.html", dict(alerts=alerts,  query=q))

@login_required(login_url='/login')
@require_http_methods(['GET'])
def search_log(request):
    q = request.GET.get('q')

    log = Logs.objects.filter(text_content__icontains=q)
    return render(request, "search_log.html", dict(logs=log, query=q))

@login_required(login_url='/login')
@require_http_methods(['GET'])
def search_date(request):
    q = request.GET.get('q')

    date = Alerts.objects.filter(time_received__lt=q)
    return render(request, "search_date.html", dict( dates=date,  query=q))