import json
import requests
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse, HttpRequest, HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import UpdateView
from .models import *
from .forms import *
from .models import Manager, Employer, Meeting, Department

from django.shortcuts import render
from .models import Manager, Employer, Meeting, Department
from django.db import transaction
import logging


def admin_home(request):
    # Get the currently logged-in user
    global total_meetings
    user = request.user

    try:
        # Assuming Admin model has a foreign key field named 'admin'
        admin = Admin.objects.get(admin=user)
    except Admin.DoesNotExist:
        # Handle the case where the user is not an admin
        admin = None

    if admin:
        # If the user is an admin, proceed with displaying meetings
        total_meetings = Meeting.objects.filter(organizer=user).count()
    total_manager = Manager.objects.all().count()
    total_employers = Employer.objects.all().count()
    # total_meetings = Meeting.objects.all().count()
    total_department = Department.objects.all().count()

    # Total Employers in Each Department
    departments = Department.objects.all()
    department_name_list = []
    employer_count_list_in_department = []

    for department in departments:
        employers_count = Employer.objects.filter(department=department).count()
        department_name_list.append(department.name)
        employer_count_list_in_department.append(employers_count)

    context = {
        'page_title': "Administrative Dashboard",
        'total_employers': total_employers,
        'total_manager': total_manager,
        'total_department': total_department,
        'total_meeting': total_meetings,
        'department_name_list': department_name_list,
        'employer_count_list_in_department': employer_count_list_in_department,
    }
    return render(request, 'hod_template/home_content.html', context)


def admin_view_profile(request):
    admin = get_object_or_404(Admin, admin=request.user)
    form = AdminForm(request.POST or None, request.FILES or None,
                     instance=admin)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                job_title = form.cleaned_data.get('job_title')
                password = form.cleaned_data.get('password') or None
                passport = request.FILES.get('profile_pic') or None
                custom_user = admin.admin
                if password != None:
                    custom_user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    custom_user.profile_pic = passport_url
                custom_user.first_name = first_name
                custom_user.last_name = last_name
                custom_user.job_title = job_title
                custom_user.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('admin_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
    return render(request, "hod_template/admin_view_profile.html", context)


def add_manager(request):
    manager_form = ManagerForm(request.POST or None, request.FILES or None)
    context = {'form': manager_form, 'page_title': 'Add Manager'}
    if request.method == 'POST':
        if manager_form.is_valid():
            first_name = manager_form.cleaned_data.get('first_name')
            last_name = manager_form.cleaned_data.get('last_name')
            address = manager_form.cleaned_data.get('address')
            email = manager_form.cleaned_data.get('email')
            gender = manager_form.cleaned_data.get('gender')
            password = manager_form.cleaned_data.get('password')
            job_title = manager_form.cleaned_data.get('job_title')
            department = manager_form.cleaned_data.get('department')
            passport = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=2, first_name=first_name, last_name=last_name,
                    profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.job_title = job_title
                user.manager.department = department
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_manager'))
            except Exception as e:
                messages.error(request, "Could Not Add: " + str(e))
        else:
            messages.error(request, "Could Not Add: ")
    return render(request, 'hod_template/add_manager_template.html', context)


def add_employer(request):
    employer_form = EmployerForm(request.POST or None, request.FILES or None)
    context = {'form': employer_form, 'page_title': 'Add Employer'}
    if request.method == 'POST':
        if employer_form.is_valid():
            first_name = employer_form.cleaned_data.get('first_name')
            last_name = employer_form.cleaned_data.get('last_name')
            address = employer_form.cleaned_data.get('address')
            email = employer_form.cleaned_data.get('email')
            gender = employer_form.cleaned_data.get('gender')
            password = employer_form.cleaned_data.get('password')
            job_title = employer_form.cleaned_data.get('job_title')
            department = employer_form.cleaned_data.get('department')
            passport = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=3, first_name=first_name, last_name=last_name,
                    profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.job_title = job_title
                user.employer.department = department
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_employer'))
            except Exception as e:
                messages.error(request, "Could Not Add: " + str(e))
        else:
            messages.error(request, "Could Not Add: ")
    return render(request, 'hod_template/add_employer_template.html', context)


def add_department(request):
    form = DepartmentForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Department'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            description = form.cleaned_data.get('description')
            try:
                department = Department()
                department.name = name
                department.description = description
                department.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_department'))
            except:
                messages.error(request, "Could Not Add")
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'hod_template/add_department_template.html', context)


def add_todolist(request):
    form = ToDoListForm(request.POST or None)
    context = {'form': form, 'page_title': 'Add Task to the list'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                todo_list = form.save(commit=False)
                todo_list.user = request.user
                todo_list.save()
                messages.success(request, "Task Created")
                return redirect(reverse('manage_todolist'))
            except Exception as e:
                messages.error(request, 'Could Not Add: ' + str(e))
        else:
            messages.error(request, 'Fill Form Properly')
    return render(request, "hod_template/add_todolist_template.html", context)


def manage_manager(request):
    allManager = CustomUser.objects.filter(user_type=2)
    context = {
        'allManager': allManager,
        'page_title': 'Manage Manager'
    }
    return render(request, "hod_template/manage_manager.html", context)


def manage_employer(request):
    employers = CustomUser.objects.filter(user_type=3)
    context = {
        'employers': employers,
        'page_title': 'Manage Employers'
    }
    return render(request, "hod_template/manage_employer.html", context)


def manage_meeting(request):
    # Filter meetings based on the currently logged-in user as the organizer
    meetings = Meeting.objects.filter(organizer=request.user)
    return render(request, 'hod_template/manage_meeting.html', {'meetings': meetings})


def manage_department(request):
    departments = Department.objects.all()
    context = {
        'departments': departments,
        'page_title': 'Manage Departments'
    }
    return render(request, "hod_template/manage_department.html", context)


def manage_todolist(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ToDoListForm(request.POST)
            if form.is_valid():
                todo_list = form.save(commit=False)
                todo_list.user = request.user
                todo_list.save()
                return redirect('manage_todolist')  # Redirect to the same page after adding the task
        else:
            form = ToDoListForm()
        user_todo_lists = TodoList.objects.filter(user=request.user)
        context = {
            'ToDoLists': user_todo_lists,
            'page_title': 'Manage ToDoLists',
            'form': form
        }
        return render(request, "hod_template/manage_todolist.html", context)
    else:
        # Redirect or handle the case where the user is not authenticated
        pass


def edit_department(request, department_id):
    instance = get_object_or_404(Department, id=department_id)
    form = DepartmentForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'department_id': department_id,
        'page_title': 'Edit Department'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            hod = form.cleaned_data.get('hod')
            description = form.cleaned_data.get('description')

            try:
                department = Department.objects.get(id=department_id)
                department.name = name
                department.hod = hod
                department.description = description
                department.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_department_template.html', context)


logger = logging.getLogger(__name__)


def delete_department(request, department_id):
    department = get_object_or_404(Department, id=department_id)

    # Collect all managers and employers belonging to the department
    managers_in_department = Manager.objects.filter(department=department)
    employers_in_department = Employer.objects.filter(department=department)

    try:
        with transaction.atomic():
            # Remove department association from all managers and employers
            managers_in_department.update(department=None)
            employers_in_department.update(department=None)

            # Now delete the department
            department.delete()

            messages.success(request, "Department deleted successfully!")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        # Log the exception for further investigation
        logger.exception("Error occurred while deleting department:")
        return HttpResponseServerError("An error occurred while deleting the department.")

    return redirect(reverse('manage_department'))


def edit_manager(request, manager_id):
    manager = get_object_or_404(Manager, id=manager_id)
    form = ManagerForm(request.POST or None, instance=manager)
    context = {
        'form': form,
        'manager_id': manager_id,
        'page_title': 'Edit Manager'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            department = form.cleaned_data.get('department')
            job_title = form.cleaned_data.get('job_title')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=manager.admin.id)
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.address = address
                user.job_title = job_title
                manager.department = department
                user.save()
                manager.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_manager', args=[manager_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please fil form properly")
    else:

        return render(request, "hod_template/edit_manager_template.html", context)


def edit_employer(request, employer_id):
    employer = get_object_or_404(Employer, id=employer_id)
    form = EmployerForm(request.POST or None, instance=employer)
    context = {
        'form': form,
        'employer_id': employer_id,
        'page_title': 'Edit Employer'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            department = form.cleaned_data.get('department')
            job_title = form.cleaned_data.get('job_title')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = employer.admin
                user.username = username
                user.email = email
                if password:
                    user.set_password(password)
                if passport:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.address = address
                user.job_title = job_title
                user.save()
                employer.department = department
                employer.save()
                messages.success(request, 'Employer updated successfully.')
                return redirect(reverse('manage_employer'))
            except Exception as e:
                messages.error(request, f'Error updating employer: {e}')
        else:
            messages.error(request, 'Please fill out the form properly.')
    else:
        return render(request, 'hod_template/edit_employer_template.html', context)


def delete_manager(request, manager_id):
    manager = get_object_or_404(CustomUser, manager__id=manager_id)
    manager.delete()
    messages.success(request, "Manager deleted successfully!")
    return redirect(reverse('manage_manager'))


@csrf_exempt
def check_email_availability(request):
    email = request.POST.get("email")
    try:
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)


def delete_employer(request, employer_id):
    employer = get_object_or_404(CustomUser, employer__id=employer_id)
    employer.delete()
    messages.success(request, "Employer deleted successfully!")
    return redirect(reverse('manage_employer'))


def delete_todolist(request, todo_id):
    todo_list = get_object_or_404(TodoList, id=todo_id, user=request.user)
    todo_list.delete()
    messages.success(request, "Task Deleted Successfully")
    return redirect('manage_todolist')


def update_todolist(request, todo_id):
    todo_list = get_object_or_404(TodoList, id=todo_id, user=request.user)
    todo_list.status = True
    todo_list.save()
    return redirect('manage_todolist')


def edit_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            meeting = form.save()
            return redirect('manage_meeting')  # Redirect to meeting detail view
    else:
        form = MeetingForm(instance=meeting)
    return render(request, 'hod_template/edit_meeting_template.html', {'form': form, 'meeting': meeting})


def delete_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    meeting.delete()
    messages.success(request, "Task Deleted Successfully")
    return redirect('manage_meeting')


def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user_type=request.user.user_type,
                        manager_department=request.user.manager.department if request.user.user_type == '2' else None)
        if form.is_valid():
            form.save(user=request.user)
            return redirect('manage_task')  # Redirect to task list page after creating task
    else:
        try:
            manager_department = request.user.manager.department if request.user.user_type == '2' else None
        except AttributeError:
            manager_department = None

        form = TaskForm(user_type=request.user.user_type, manager_department=manager_department)

    return render(request, 'hod_template/add_task_template.html', {'form': form})


def manage_task(request):
    # Filter tasks based on the currently logged-in user as the manager
    tasks = Task.objects.filter(manager=request.user)
    return render(request, 'hod_template/manage_task.html', {'tasks': tasks})


def edit_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('manage_task')
    else:
        form = TaskForm(instance=task)
    return render(request, 'hod_template/edit_task_template.html', {'form': form})


def delete_task(request, task_id):
    meeting = get_object_or_404(Task, id=task_id)
    meeting.delete()
    messages.success(request, "Task Deleted Successfully")
    return redirect('manage_task')


def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.completed = True
    task.save()
    return redirect('manage_task')


def create_meeting(request):
    filter_form = FilterParticipantsForm()  # Initialize filter form outside the if-else block

    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.organizer = request.user
            meeting.save()
            form.save_m2m()
            return redirect('manage_meeting')  # Redirect to meeting detail view
        else:
            # Form is not valid, handle errors
            participants = CustomUser.objects.none()  # Initialize participants queryset
            return render(request, 'hod_template/create_meeting_template.html', {
                'form': form,
                'filter_form': filter_form,
                'participants': participants,
            })

    else:
        form = MeetingForm()

    return render(request, 'hod_template/create_meeting_template.html', {
        'form': form,
        'filter_form': filter_form,
    })


def filter_participants(request):
    if request.method == 'POST':
        form = FilterParticipantsForm(request.POST)
        if form.is_valid():
            user_type = form.cleaned_data.get('user_type')
            department = form.cleaned_data.get('department')
            participants = CustomUser.objects.none()  # Initialize participants queryset

            if department:
                if user_type == '1':  # HOD
                    participants = CustomUser.objects.filter(manager__department=department, user_type=user_type)
                elif user_type == '2':  # Manager
                    participants = CustomUser.objects.filter(manager__department=department, user_type=user_type)
                elif user_type == '3':  # Employer
                    participants = CustomUser.objects.filter(employer__department=department, user_type=user_type)
            else:
                participants = CustomUser.objects.filter(user_type=user_type)

            # Convert queryset to list of dictionaries
            participants_data = [
                {'id': participant.id, 'first_name': participant.first_name, 'last_name': participant.last_name}
                for participant in participants]

            return JsonResponse({'participants': participants_data})
        else:
            # If form is not valid, return errors
            return JsonResponse({'errors': form.errors}, status=400)

    else:
        form = FilterParticipantsForm()

    return render(request, 'hod_template/create_meeting_template.html', {'filter_form': form})


def admin_notify_manager(request):
    manager = CustomUser.objects.filter(user_type=2)
    context = {
        'page_title': "Send Notifications To Manager",
        'allManager': manager
    }
    return render(request, "hod_template/manager_notification.html", context)


@csrf_exempt
def send_manager_notification(request):
    if request.method == 'POST':
        manager_id = request.POST.get('manager_id')
        message = request.POST.get('message')

        # Ensure both manager_id and message are provided
        if manager_id is not None and message:
            manager = get_object_or_404(Manager, id=manager_id)
            # Accessing the associated CustomUser instance
            manager_user = manager.admin

            try:
                # Replace this URL with your FCM endpoint URL
                fcm_url = "https://fcm.googleapis.com/fcm/send"

                # Construct the payload for FCM
                fcm_payload = {
                    'notification': {
                        'title': "Manager Management System",
                        'body': message,
                        'click_action': reverse('manager_view_notification'),
                        'icon': static('dist/img/AdminLTELogo.png')
                    },
                    'to': manager_user.fcm_token,  # Accessing fcm_token from CustomUser
                    'sender': request.user.username  # Add the sender username
                }

                # Replace this with your FCM server key
                fcm_headers = {
                    'Authorization': 'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                    'Content-Type': 'application/json'}

                # Send the notification to FCM server
                response = requests.post(fcm_url, data=json.dumps(fcm_payload), headers=fcm_headers)

                # Ensure the request was successful
                response.raise_for_status()

                # Save the notification in the database
                notification = NotificationManagers(sender=request.user, managers=manager, message=message)
                notification.save()

                return JsonResponse({'success': True})  # Change 'status' to 'success'
            except Exception as e:
                print("Error sending notification:", e)
                return JsonResponse({'success': False, 'error': str(e)})  # Change 'status' to 'success'
        else:
            return JsonResponse({'success': False, 'error': 'Missing manager_id or message'}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


def admin_notify_employer(request):
    employer = CustomUser.objects.filter(user_type=3)
    context = {
        'page_title': "Send Notifications To Employers",
        'employers': employer
    }
    return render(request, "hod_template/employer_notification.html", context)


@csrf_exempt
def send_employer_notification(request):
    if request.method == 'POST':
        employer_id = request.POST.get('employer_id')
        message = request.POST.get('message')

        # Ensure both manager_id and message are provided
        if employer_id is not None and message:
            employer = get_object_or_404(Employer, id=employer_id)
            # Accessing the associated CustomUser instance
            employer_user = employer.admin

            try:
                # Replace this URL with your FCM endpoint URL
                fcm_url = "https://fcm.googleapis.com/fcm/send"

                # Construct the payload for FCM
                fcm_payload = {
                    'notification': {
                        'title': "Employer Management System",
                        'body': message,
                        'click_action': reverse('employer_view_notification'),
                        'icon': static('dist/img/AdminLTELogo.png')
                    },
                    'to': employer_user.fcm_token,  # Accessing fcm_token from CustomUser
                    'sender': request.user.username  # Add the sender username
                }

                # Replace this with your FCM server key
                fcm_headers = {
                    'Authorization': 'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                    'Content-Type': 'application/json'}

                # Send the notification to FCM server
                response = requests.post(fcm_url, data=json.dumps(fcm_payload), headers=fcm_headers)

                # Ensure the request was successful
                response.raise_for_status()

                # Save the notification in the database
                notification = NotificationEmployers(sender=request.user, employers=employer, message=message)
                notification.save()

                return JsonResponse({'success': True})  # Change 'status' to 'success'
            except Exception as e:
                print("Error sending notification:", e)
                return JsonResponse({'success': False, 'error': str(e)})  # Change 'status' to 'success'
        else:
            return JsonResponse({'success': False, 'error': 'Missing employer_id or message'}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@login_required
def admin_receive_message(request):
    receiver = request.user
    received_messages = Message.objects.filter(receiver=receiver)

    if request.method == 'POST':
        if 'message_id' in request.POST:
            message_id = request.POST.get('message_id')
            reply_text = request.POST.get('reply')

            try:
                message = get_object_or_404(Message, id=message_id, receiver=receiver)
                message.reply = reply_text
                message.save()
                messages.success(request, "Reply sent successfully")
            except Exception as e:
                messages.error(request, f"Could not send reply: {e}")
            return redirect(reverse('receive_message'))

    return render(request, "hod_template/manage_message_template.html", {
        'received_messages': received_messages,
        'page_title': 'Receive message'
    })


# def display_admin_meeting(request):
#     # Get the currently logged-in user
#     user = request.user
#     # Filter tasks assigned to the logged-in user
#     meetings = Meeting.objects.filter(participants=user)
#
#     # Render the template with the filtered tasks
#     return render(request, 'hod_template/manage_Admeeting.html', {'meetings': meetings})
logger = logging.getLogger(__name__)


# def display_admin_meeting(request):
#     # Get the currently logged-in administrator
#     admin = request.user
#     logger.info(f"Admin: {admin}")
#
#     # Filter meetings where the current administrator is the organizer
#     meetings = Meeting.objects.filter(organizer=admin)
#
#     logger.info(f"Meetings: {meetings}")
#
#     # Render the template with the filtered meetings
#     return render(request, 'hod_template/manage_Admeeting.html', {'meetings': meetings})
