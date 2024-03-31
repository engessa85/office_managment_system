import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites import requests
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import (HttpResponseRedirect, get_object_or_404, redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.templatetags.static import static
from jsonschema.exceptions import ValidationError

from .forms import *
from .models import *


def manager_home(request):
    manager = get_object_or_404(Manager, admin=request.user)
    total_employers = Employer.objects.filter(department=manager.department).count()
    total_meetings = Meeting.objects.filter(participants=manager.admin).count()
    tasks = Task.objects.filter(user=request.user, user__user_type=2)
    total_task = tasks.count()
    total_message = Message.objects.filter(receiver=manager.admin).count()

    context = {
        'page_title': f'Manager Panel - {manager.admin.last_name} ({manager.department})',
        'total_employers': total_employers,
        'total_meetings': total_meetings,
        'total_task': total_task,
        'total_message': total_message,
    }
    return render(request, 'manager_template/home_content.html', context)


@csrf_exempt
def manager_fcmtoken(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        if token:
            try:
                manager_user = get_object_or_404(CustomUser, id=request.user.id)
                manager_user.fcm_token = token
                manager_user.save()
                return JsonResponse({'status': 'success'})
            except CustomUser.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        else:
            return JsonResponse({'status': 'error', 'message': 'Token is required'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


def manager_view_profile(request):
    manager = get_object_or_404(Manager, admin=request.user)
    form = ManagerEditForm(request.POST or None, request.FILES or None, instance=manager)
    context = {'form': form, 'page_title': 'View/Update Profile'}
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                job_title = form.cleaned_data.get('job_title')
                passport = request.FILES.get('profile_pic') or None
                admin = manager.admin
                if password != None:
                    admin.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url
                admin.first_name = first_name
                admin.last_name = last_name
                admin.address = address
                admin.gender = gender
                admin.job_title = job_title
                admin.save()
                manager.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('manager_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
                return render(request, "manager_template/manager_view_profile.html", context)
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
            return render(request, "manager_template/manager_view_profile.html", context)

    return render(request, "manager_template/manager_view_profile.html", context)


def add_todolist_manager(request):
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
    return render(request, "manager_template/add_todolist_template.html", context)


def manage_todolist_manager(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ToDoListForm(request.POST)
            if form.is_valid():
                todo_list = form.save(commit=False)
                todo_list.user = request.user
                todo_list.save()
                return redirect('manage_todolist_manager')  # Redirect to the same page after adding the task
        else:
            form = ToDoListForm()
        user_todo_lists = TodoList.objects.filter(user=request.user)
        context = {
            'ToDoLists': user_todo_lists,
            'page_title': 'Manage ToDoLists',
            'form': form
        }
        return render(request, "manager_template/manage_todolist.html", context)
    else:
        # Redirect or handle the case where the user is not authenticated
        pass


def delete_todolist_manager(request, todo_id):
    todo_list = get_object_or_404(TodoList, id=todo_id, user=request.user)
    todo_list.delete()
    messages.success(request, "Task Deleted Successfully")
    return redirect('manage_todolist_manager')


def update_todolist_manager(request, todo_id):
    todo_list = get_object_or_404(TodoList, id=todo_id, user=request.user)
    todo_list.status = True
    todo_list.save()
    return redirect('manage_todolist_manager')


def add_task_manager(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user_type=request.user.user_type,
                        manager_department=request.user.manager.department if request.user.user_type == '2' else None)
        if form.is_valid():
            form.save(user=request.user)
            return redirect('manage_task_manager')  # Redirect to task list page after creating task
    else:
        try:
            manager_department = request.user.manager.department if request.user.user_type == '2' else None
        except AttributeError:
            manager_department = None

        form = TaskForm(user_type=request.user.user_type, manager_department=manager_department)

    return render(request, 'manager_template/add_task_template.html', {'form': form})


def manage_task_manager(request):
    user = request.user  # Get the currently logged-in user
    tasks = Task.objects.filter(manager=user)  # Filter tasks assigned to the logged-in user
    return render(request, 'manager_template/manage_task.html', {'tasks': tasks})


def edit_task_manager(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('manage_task_manager')
    else:
        form = TaskForm(instance=task)
    return render(request, 'manager_template/edit_task_template.html', {'form': form})


def delete_task_manager(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    messages.success(request, "Task Deleted Successfully")
    return redirect('manage_task_manager')


@login_required
def manage_meeting_manager(request):
    # Assuming you have a ForeignKey field named 'organizer' in your Meeting model
    # that points to the User model
    meetings = Meeting.objects.filter(organizer=request.user)
    return render(request, 'manager_template/manage_meetingM.html', {'meetings': meetings})


def create_meeting_manager(request):
    filter_form = FilterParticipantsForm()  # Initialize filter form outside the if-else block
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.organizer = request.user
            meeting.save()
            form.save_m2m()
            return redirect('manage_meeting_manager')  # Redirect to meeting detail view
        else:
            # Form is not valid, handle errors
            participants = CustomUser.objects.none()  # Initialize participants queryset
            return render(request, 'manager_template/create_meetingM_template.html', {
                'form': form,
                'filter_form': filter_form,
                'participants': participants,
            })

    else:
        form = MeetingForm()

    return render(request, 'manager_template/create_meetingM_template.html', {
        'form': form,
        'filter_form': filter_form,
    })


# def filter_participants_manager(request):
#     if request.method == 'POST':
#         form = FilterParticipantsForm(request.POST)
#         if form.is_valid():
#             user_type = form.cleaned_data.get('user_type')
#             department = form.cleaned_data.get('department')
#             participants = CustomUser.objects.none()  # Initialize participants queryset
#
#             if department:
#                 if user_type == '1':  # HOD
#                     participants = CustomUser.objects.filter(manager__department=department, user_type=user_type)
#                 elif user_type == '2':  # Manager
#                     participants = CustomUser.objects.filter(manager__department=department, user_type=user_type)
#                 elif user_type == '3':  # Employer
#                     participants = CustomUser.objects.filter(employer__department=department, user_type=user_type)
#             else:
#                 participants = CustomUser.objects.filter(user_type=user_type)
#
#             # Convert queryset to list of dictionaries
#             participants_data = [
#                 {'id': participant.id, 'first_name': participant.first_name, 'last_name': participant.last_name}
#                 for participant in participants]
#
#             return JsonResponse({'participants': participants_data})
#         else:
#             # If form is not valid, return errors
#             return JsonResponse({'errors': form.errors}, status=400)
#
#     else:
#         form = FilterParticipantsForm()
#
#     return render(request, 'manager_template/create_meetingM_template.html', {'filter_form': form})
@login_required
def filter_participants_manager(request):
    if request.method == 'POST':
        form = FilterParticipantsForm(request.POST)
        if form.is_valid():
            user_type = form.cleaned_data.get('user_type')
            department = form.cleaned_data.get('department')

            # Initialize participants queryset
            participants = CustomUser.objects.exclude(id=request.user.id)

            if department:
                if user_type == '1':  # HOD
                    participants = participants.filter(manager__department=department, user_type=user_type)
                elif user_type == '2':  # Manager
                    participants = participants.filter(manager__department=department, user_type=user_type)
                elif user_type == '3':  # Employer
                    participants = participants.filter(employer__department=department, user_type=user_type)
            else:
                participants = participants.filter(user_type=user_type)

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

    return render(request, 'manager_template/create_meetingM_template.html', {'filter_form': form})

def edit_meeting_manager(request, meeting_id):
    # Retrieve the meeting instance or raise 404 if not found
    meeting = get_object_or_404(Meeting, pk=meeting_id)

    if request.method == 'POST':
        # If form submitted via POST, process the data
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            # If form data is valid, save the changes to the meeting instance
            meeting = form.save()
            # Redirect to a view to manage meetings (replace 'manage_meeting_manager' with the appropriate view name)
            return redirect('manage_meeting_manager')  # Redirect to meeting detail view
    else:
        # If not a POST request, create a form with the meeting instance data
        form = MeetingForm(instance=meeting)

    # Render the template with the form and meeting instance
    return render(request, 'manager_template/edit_meeting_template.html', {'form': form, 'meeting': meeting})


def delete_meeting_manager(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    meeting.delete()
    messages.success(request, "Task Deleted Successfully")
    return redirect('manage_meeting_manager')


def display_user_tasks(request):
    # Get the currently logged-in user
    user = request.user
    # Filter tasks assigned to the logged-in user
    tasks = Task.objects.filter(user=user)

    # Render the template with the filtered tasks
    return render(request, 'manager_template/manager_manage_tasks.html', {'tasks': tasks})


def display_user_meeting(request):
    # Get the currently logged-in user
    user = request.user
    # Filter tasks assigned to the logged-in user
    meetings = Meeting.objects.filter(participants=user)

    # Render the template with the filtered tasks
    return render(request, 'manager_template/manage_Mymeeting.html', {'meetings': meetings})


def update_mytask(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.completed = True  # Assuming 'completed' is the field representing task status
    task.save()
    return redirect('display_user_tasks')  # Redirect back to the task list page


def manager_view_notification(request):
    manager = get_object_or_404(Manager, admin=request.user)
    notifications = NotificationManagers.objects.filter(managers=manager)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "manager_template/manager_view_notification.html", context)


@login_required
def send_message(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect if user is not authenticated

    form = MessageForm(request.POST or None, user=request.user)  # Pass user to the form
    sent_messages = Message.objects.filter(sender=request.user, cleared=False)

    if request.method == 'POST':
        if form.is_valid():
            try:
                # Save the message with sender and receiver information
                message = form.save(commit=False)
                message.sender = request.user
                message.save()
                messages.success(request, "Message sent successfully")
                return redirect(reverse('send_message'))
            except Exception as e:
                messages.error(request, f"Could not send message: {e}")
        else:
            messages.error(request, "Form has errors!")

    return render(request, "manager_template/manager_send_messages.html", {
        'form': form,
        'sent_messages': sent_messages,
        'page_title': 'Send message'
    })


@login_required
def receive_message(request):
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

    return render(request, "manager_template/manager_Receiver_messages.html", {
        'received_messages': received_messages,
        'page_title': 'Receive message'
    })


@login_required
def manager_delete_send_message(request, message_id):
    try:
        message = Message.objects.get(id=message_id, sender=request.user)
        message.delete()
        messages.success(request, "Message deleted successfully")
    except Message.DoesNotExist:
        messages.error(request, "Message does not exist")
    except Exception as e:
        messages.error(request, f"Could not delete message: {e}")

    return redirect(reverse('send_message'))


def manager_edit_message(request, message_id):
    # Get the message object to be edited
    message = get_object_or_404(Message, id=message_id, sender=request.user)

    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Message edited successfully")
                return redirect(reverse('send_message'))
            except Exception as e:
                messages.error(request, f"Could not edit message: {e}")
        else:
            messages.error(request, "Form has errors!")
    else:
        # Populate the form with the current message data
        form = MessageForm(instance=message)

    return render(request, "manager_template/manager_edit_message.html", {
        'form': form,
        'message': message,
        'page_title': 'Edit message'
    })


@login_required
def clear_send_messages(request):
    if request.method == 'POST':
        message_ids = request.POST.getlist('message_ids')  # Retrieve selected message IDs
        try:
            # Update the cleared status of messages
            messages_to_clear = Message.objects.filter(id__in=message_ids)
            messages_to_clear.update(cleared=True)
            messages.success(request, "Messages cleared successfully")
        except Exception as e:
            messages.error(request, f"Could not clear messages: {e}")

    # Redirect back to the previous page or any specific page after clearing messages
    return redirect(request.META.get('HTTP_REFERER', reverse(
        'send_message')))  # Redirect back to the previous page if available, or 'send_message' if not


@login_required
def manager_create_project(request):
    manager_department = None
    try:
        manager_department = request.user.manager.department if request.user.user_type == '2' else None
    except AttributeError:
        pass

    if request.method == 'POST':
        form = ProjectForm(request.POST, manager_department=manager_department)
        if form.is_valid():
            project = form.save(commit=False)
            project.project_manager = request.user
            form.save(user=request.user)
            return redirect('manager_manage_project')  # Redirect to task list page after creating task
    else:
        form = ProjectForm(manager_department=manager_department)

    return render(request, 'manager_template/create_project_template.html', {'form': form})


@login_required
def manager_manage_project(request):
    # Filter projects based on the logged-in user
    projects = Project.objects.filter(project_manager=request.user)
    return render(request, 'manager_template/manage_project.html', {'projects': projects})


@login_required
def manager_edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project,
                           manager_department=request.user.manager.department if request.user.user_type == '2' else None)
        if form.is_valid():
            form.save(user=request.user)
            return redirect('manager_manage_project')  # Redirect to project detail page
    else:
        form = ProjectForm(instance=project,
                           manager_department=request.user.manager.department if request.user.user_type == '2' else None)

    return render(request, 'manager_template/edit_project_template.html', {'form': form, 'project': project})


def manager_delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project.delete()
    messages.success(request, "Project Deleted Successfully")
    return redirect('manager_manage_project')  # Corrected URL name


@login_required
def upload_file(request, project_id):
    project = Project.objects.get(id=project_id)
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = form.save(commit=False)
            new_file.project = project
            new_file.uploaded_by = request.user  # Set uploaded_by to the currently logged-in user
            new_file.save()
            return redirect('manager_manage_project')
    else:
        form = FileUploadForm()
    return render(request, 'manager_template/upload_file.html', {'form': form})


def project_files(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    files = project.documents.all()  # Assuming 'documents' is the related_name for files in Project model
    return render(request, 'manager_template/project_files.html', {'project': project, 'files': files})


def manager_delete_file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    project_id = file.project_id  # Get the project ID before deleting the file
    file.delete()
    messages.success(request, "File Deleted Successfully")
    return redirect(reverse('project_files', kwargs={'project_id': project_id}))
