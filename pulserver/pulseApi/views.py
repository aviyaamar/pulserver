import json
import pprint
import datetime
import base64
import uuid

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import render

from pulseApp import models


@csrf_exempt
@require_POST
def process_commands(request, auth_key, computer_auth):
    # Find the client
    company = models.Company.objects.filter(auth_key=auth_key).first()
    if not company:
        return HttpResponse(status=500)
    # Find the computer
    computer = models.Computers.objects.filter(auth_key=computer_auth).first()
    if not computer:
        return HttpResponse(status=500)

    # Parse the json data
    data = json.loads(request.body.decode("utf-8"))

    command_id = data["command_id"]
    command_results = data["results"]

    command = models.Command.objects.get(id=command_id, computer=computer)
    command.completed = True
    command.errors = not command_results["success"]
    command.outcome = command_results["output"]

    command.save()

    # Handle apt list specific logic
    if command.command == "apt list --installed":
        # Parse computer software
        process_computer_software(computer, command.outcome)

        # Mark computer not busy
        computer.upgrade_in_progress = False
        computer.save()

    return JsonResponse(dict(success=True))

def process_computer_software(computer, apt_output):
    """
    curl/now 7.47.0-1ubuntu2.7 amd64 [installed,upgradable to: 7.47.0-1ubuntu2.8]
    libcurl3/now 7.47.0-1ubuntu2.7 amd64 [installed,upgradable to: 7.47.0-1ubuntu2.8
    libcurl3-gnutls/now 7.47.0-1ubuntu2.7 amd64 [installed,upgradable to: 7.47.0-1ub
    python-pycurl/xenial,now 7.43.0-1ubuntu1 amd64 [installed,automatic]
    python3-pycurl/xenial,now 7.43.0-1ubuntu1 amd64 [installed]
    """
    # Delete all computer software
    models.Software.objects.filter(computer=computer).delete()

    # Parse new software
    new_softwares = []
    for line in base64.b64decode(apt_output).decode("utf8").splitlines():
        tokens = line.split(" ", 3)
        if 4 != len(tokens):
            continue

        software_name = tokens[0].split("/")[0]
        software_current_version = tokens[1]
        software_upgrade_version = None
        upgrade_token = next((token for token in tokens[3][1:-1].split(",") if token.startswith("upgradable to: ")), None)
        if upgrade_token:
            software_upgrade_version = upgrade_token[len("upgradable to: "):]

        new_softwares.append(
            models.Software(
                computer=computer,
                name=software_name,
                current_version=software_current_version,
                upgrade_version=software_upgrade_version
            )
        )

    models.Software.objects.bulk_create(new_softwares)

@csrf_exempt
@require_POST
def process_statistics(request, auth_key, computer_auth):
    # Find the client
    company = models.Company.objects.filter(auth_key=auth_key).first()
    if not company:
        return HttpResponse(status=500)
    # Find the computer
    computer = models.Computers.objects.filter(auth_key=computer_auth).first()
    if not computer:
        return HttpResponse(status=500)

    # Parse the json data
    data = json.loads(request.body.decode("utf-8"))


    stat_type = data['statistics_type']
    create_time = datetime.datetime.utcfromtimestamp(data["create_time"])
    if "system" == stat_type:
        computer.version = data["statistics_data"]["version"]
        computer.operating_system = data["statistics_data"]["os"]
        computer.computer_name = data["statistics_data"]["name"]
        computer.cpu = data["statistics_data"]["cpu"]
        computer.save()
    elif "log" == stat_type:
        log_data = data["statistics_data"]
        for line in log_data["lines"]:
            log_object = models.Logs.objects.create(
                text_content=line,
                path=log_data["file_path"],
                time_created=create_time,
                computer=computer,
                log_type=stat_type,
                process=False,
            )
            log_object.save()
    else:

        stat_data = data["statistics_data"]
        stat_object = models.Statistics.objects.create(
            computer=computer,
            time_created=create_time,
            type=stat_type,
            content=json.dumps(stat_data)
        )
        stat_object.save()

    # Do alers
    analyze_cpus_and_create_alerts(company, computer)
    #   analyze_logs_and_create_alerts(company, computer)
    analyze_memory_and_create_alerts(company, computer)
    analyze_disks_and_create_alerts(company, computer)

    return JsonResponse(dict(success=True))


@csrf_exempt
@require_GET
def query_commands(request, auth_key, computer_auth):
    # Find the client
    company = models.Company.objects.filter(auth_key=auth_key).first()
    if not company:
        return HttpResponse(status=500)
    # Find the computer
    computer = models.Computers.objects.filter(auth_key=computer_auth).first()
    if not computer:
        return HttpResponse(status=500)

    # Load all the not sent commands
    commands = models.Command.objects.filter(computer=computer, sent=False)
    sent_commands = []
    for command in commands:
        # Build command to send
        sent_commands.append(dict(
            id=command.id,
            command=command.command,
        ))

        # Update command as set
        command.sent = True
        command.save()

    return JsonResponse(dict(success=True, commands=sent_commands))


@csrf_exempt
@require_POST
def register_comp(request, auth_key):
    # Find the client
    company = models.Company.objects.filter(auth_key=auth_key).first()
    if not company:
        return HttpResponse(status=500)

    computer = models.Computers.objects.create(
        company=company,
        auth_key=uuid.uuid4().hex,
    )

    computer.save()

    return JsonResponse(dict(auth_key=computer.auth_key))

"""cpu alerts"""
def analyze_cpus_and_create_alerts(company, computer):
    # Read cpus check for alerts
    # Create cpu alerts
    severity_level = None
    alert_description = None

    """70%- lightalert , 80%- mediumalert 90%- danger"""
    diff_avg = diff_cpu_average(computer)
    import pprint
    pprint.pprint(diff_avg)
    if diff_avg:
        value_max = max(diff_avg.values())
        if 5 < value_max <= 10:
            severity_level = "light alert"
            alert_description = " cpu increase to " + str(value_max) + "!"

        elif 10 < value_max <= 30:
            severity_level = "medium alert"
            alert_description = "cpu increase to " + str(value_max) + "!"

        elif value_max > 30:
            severity_level = "huston we have a problem"
            alert_description = "cpu increase to " + str(value_max) + "!"

        if severity_level and alert_description:
            alerts_object = update_or_create_alert(computer, "cpu", severity_level, alert_description)
            alerts_object.save()


def avg(values):
    return sum(values) / len(values)


def get_cpu_average(computer, count):
    all_cpu_entries = [json.loads(x.content)["cpus"] for x in models.Statistics.objects.filter(computer=computer, type="cpu").order_by('-time_created')[:count]]
    all_cpus_name = set(cpu_name for entry in all_cpu_entries for cpu_name in entry.keys())
    return {cpu_name: avg([entry[cpu_name] for entry in all_cpu_entries if cpu_name in entry]) for cpu_name in
            all_cpus_name}


def diff_cpu_average(computer):
    avg_10 = get_cpu_average(computer, 10)
    avg_100 = get_cpu_average(computer, 100)
    import pprint
    pprint.pprint(avg_10)
    pprint.pprint(avg_100)
    return {cpu_name: avg_100[cpu_name] * 100 / cpu_value - 100 for cpu_name, cpu_value in avg_10.items()}

"""logs alerts"""
def analyze_logs_and_create_alerts(company, computer):
    severity_level = None
    alert_description = None

    log_alerts = run_last_logs(computer)
    if log_alerts:
        severity_level = "log in problem"
        alert_description = str(log_alerts)
        alerts_object = models.Alerts.objects.create(
            computer=computer,
            severity_level=severity_level,
            alert_description=alert_description,
            read_by_user=False
        )
        alerts_object.save()


def run_last_logs(computer):
    all_logs = [n.text_content for n in models.Logs.objects.filter(computer=computer, log_type="log", text_content__contains="3 incorrect password").order_by(
        "-time_created")[:10]]
    return all_logs

"""memory alerts"""
def analyze_memory_and_create_alerts(company, computer):
    severity_level = None
    alert_description = None

    vm_stats = diff_memory_average(computer)
    if vm_stats:

        if 10 < vm_stats["available memory"] < 15 and 10 < vm_stats["memory percent"] < 15:
            severity_level = "light alert"
            alert_description = str(vm_stats) + " virtual memory percent"

        elif 15 < vm_stats["available memory"] < 20 and 15 < vm_stats["memory percent"] < 20:
            severity_level = "medium alert"
            alert_description = str(vm_stats) + " virtual memory percent"

        elif 20 < vm_stats["available memory"] < 25 and 20 < vm_stats["memory percent"] < 25:
            severity_level = "medium alert"
            alert_description = str(vm_stats) + " virtual memory percent"

        if severity_level and alert_description:
            alerts_object = update_or_create_alert(computer, "memory", severity_level, alert_description)
            alerts_object.save()


def avg_memo(values):
    return sum(values) / len(values)

def get_memory_average(computer, count):
    all_memory_entries = [json.loads(x.content) for x in models.Statistics.objects.filter(computer=computer, type="virtual memory").order_by('-time_created')[:count]]
    all_memory_name = set(memory_name for entry in all_memory_entries for memory_name in entry.keys())
    return {memory_name: avg_memo([entry[memory_name] for entry in all_memory_entries if memory_name in entry]) for memory_name in all_memory_name}


def diff_memory_average(computer):
    avg_10 = get_memory_average(computer, 5)
    avg_100 = get_memory_average(computer, 10)
    return {memory_name: avg_100[memory_name] * 100 / memory_value - 100 for memory_name, memory_value in avg_10.items()}
#def run_memory_check(computer):
#    memo = [json.loads(x.content) for x in
#            models.Statistics.objects.filter(computer=computer, type="virtual memory").order_by("-time_created")[:10]]

"""Disk alerts"""
def analyze_disks_and_create_alerts(company, computer):
    percent = disk_space(computer)
    if percent:
        for k, v in percent.items():

            severity_level = None
            alert_description = None

            if 30 < v < 75:
                severity_level = "light alert"
                alert_description = k+" "+str(v) + " disk memory"

            elif 75 < v < 80:
                severity_level = "medium alert"
                alert_description = k+" "+str(v) + " disk memory"

            elif 80 < v:
                severity_level = "danger"
                alert_description = k+" "+str(v) + " disk memory"

            if severity_level and alert_description:
                alerts_object = update_or_create_alert(computer, "disk-" + k, severity_level, alert_description)
                alerts_object.save()


def update_or_create_alert(computer, key, severity_level, description):
    alerts_object = models.Alerts.objects.filter(
        computer=computer,
        key=key,
        read_by_user=False
    ).first()

    # Check if the same alert already exists and not acknowledged by user
    if alerts_object:
        alerts_object.severity_level = severity_level
        alerts_object.alert_description = description

    else:
        alerts_object = models.Alerts.objects.create(
            computer=computer,
            key=key,
            severity_level=severity_level,
            alert_description=description,
            read_by_user=False
        )

    return alerts_object


def disk_space(computer):
    disk_percent = {}
    all_disks = [{key: value for key, value in json.loads(x.content).items() if not key.startswith("/dev/loop")} for x in models.Statistics.objects.filter(computer=computer, type="disk").order_by('-time_created')[:1]]
    if all_disks:
        for k, v in all_disks[0].items():
            disk_percent[k] = v["percent"]
    return disk_percent




"""
apt update && apt list --upgradeable

# Single package
apt install -y --only-upgrade <NAME>

# All packages

"""