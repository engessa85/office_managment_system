from django.urls import path

from main_app import views, manager_views, employer_views
from . import hod_views

urlpatterns = [
    path("", views.login_page, name='login_page'),
    path("doLogin/", views.doLogin, name='user_login'),
    path("logout_user/", views.logout_user, name='user_logout'),
    path("admin/home/", hod_views.admin_home, name='admin_home'),
    path("admin_view_profile/", hod_views.admin_view_profile, name='admin_view_profile'),
    path("firebase-messaging-sw.js", views.showFirebaseJS, name='showFirebaseJS'),
    # admin URL
    path("employer/add/", hod_views.add_employer, name='add_employer'),
    path("todolist/add/", hod_views.add_todolist, name='add_todolist'),
    path("manager/add/", hod_views.add_manager, name='add_manager'),
    path("manager/manage/", hod_views.manage_manager, name='manage_manager'),
    path("employer/manage/", hod_views.manage_employer, name='manage_employer'),
    path("todolist/manage/", hod_views.manage_todolist, name='manage_todolist'),
    path("todolist/delete/<int:todo_id>/", hod_views.delete_todolist, name='delete_todolist'),
    path("todolist/update/<int:todo_id>/", hod_views.update_todolist, name='update_todolist'),
    path("meeting/create/", hod_views.create_meeting, name='create_meeting'),
    path("department/manage/", hod_views.manage_department, name='manage_department'),
    path("meeting/manage/", hod_views.manage_meeting, name='manage_meeting'),
    path("department/add/", hod_views.add_department, name='add_department'),
    path("department/edit/<int:department_id>/", hod_views.edit_department, name='edit_department'),
    path("department/delete/<int:department_id>/", hod_views.delete_department, name='delete_department'),
    path("check_email_availability/", hod_views.check_email_availability, name="check_email_availability"),
    path("manager/edit/<int:manager_id>/", hod_views.edit_manager, name='edit_manager'),
    path("manager/delete/<int:manager_id>/", hod_views.delete_manager, name='delete_manager'),
    path('employer/edit/<int:employer_id>/', hod_views.edit_employer, name='edit_employer'),
    path("employer/delete/<int:employer_id>/", hod_views.delete_employer, name='delete_employer'),
    path('meeting/edit/<int:meeting_id>/', hod_views.edit_meeting, name='edit_meeting'),
    path("meeting/delete/<int:meeting_id>/", hod_views.delete_meeting, name='delete_meeting'),
    path("task/add/", hod_views.add_task, name='add_task'),
    path("task/manage/", hod_views.manage_task, name='manage_task'),
    path('task/edit/<int:task_id>/', hod_views.edit_task, name='edit_task'),
    path('task/update/<int:task_id>/', hod_views.update_task_status, name='update_task_status'),
    path("task/delete/<int:task_id>/", hod_views.delete_task, name='delete_task'),
    path('meeting/filter_participants/', hod_views.filter_participants, name='filter_participants'),
    path("admin_receive_message/", hod_views.admin_receive_message,
         name="admin_receive_message",),
    path("admin_notify_manager/", hod_views.admin_notify_manager,
         name='admin_notify_manager'),
    path("send_manager_notification/", hod_views.send_manager_notification,
         name='send_manager_notification'),
    path("admin_notify_employer/", hod_views.admin_notify_employer,
         name='admin_notify_employer'),
    path("send_mployer_notification/", hod_views.send_employer_notification,
         name='send_employer_notification'),
    # path('display_admin_meeting/', hod_views.display_admin_meeting, name='display_admin_meeting'),





    #
    # # manager URL
    path("manager/home/", manager_views.manager_home, name='manager_home'),
    path("manager/view/profile/", manager_views.manager_view_profile,
         name='manager_view_profile'),
    path("manager/todolist/add/", manager_views.add_todolist_manager, name='add_todolist_manager'),
    path("manager/todolist/manage/", manager_views.manage_todolist_manager, name='manage_todolist_manager'),
    path("manager/todolist/delete/<int:todo_id>/", manager_views.delete_todolist_manager, name='delete_todolist_manager'),
    path("manager/todolist/update/<int:todo_id>/", manager_views.update_todolist_manager, name='update_todolist_manager'),
    path("manager/task/add/", manager_views.add_task_manager, name='add_task_manager'),
    path("manager/task/manage/", manager_views.manage_task_manager, name='manage_task_manager'),
    path('manager/task/edit/<int:task_id>/', manager_views.edit_task_manager, name='edit_task_manager'),
    path("manager/task/delete/<int:task_id>/", manager_views.delete_task_manager, name='delete_task_manager'),
    path("manager/meeting/create/", manager_views.create_meeting_manager, name='create_meeting_manager'),
    path('manager/meeting/edit/<int:meeting_id>/', manager_views.edit_meeting_manager, name='edit_meeting_manager'),
    path("manager/meeting/delete/<int:meeting_id>/", manager_views.delete_meeting_manager, name='delete_meeting_manager'),
    path("manager/meeting/manage/", manager_views.manage_meeting_manager, name='manage_meeting_manager'),
    path('manager/meeting/filter_participants_manager/', manager_views.filter_participants_manager, name='filter_participants_manager'),
    path("manager/fcmtoken/", manager_views.manager_fcmtoken, name='manager_fcmtoken'),
    path("manager/view/notification/", manager_views.manager_view_notification,
         name="manager_view_notification"),
    path('manager/mytask/update/<int:task_id>/', manager_views.update_mytask, name='update_mytask'),
    path('manager/display_user_tasks/', manager_views.display_user_tasks, name='display_user_tasks'),
    path('manager/display_user_meeting/', manager_views.display_user_meeting, name='display_user_meeting'),
    path('manager/receive_message/', manager_views.receive_message, name='receive_message'),
    path('manager/send_message/', manager_views.send_message, name='send_message'),
    path('manager/delete_send_message/<int:message_id>/', manager_views.manager_delete_send_message, name='manager_delete_send_message'),
    path('manager/send_message/edit/<int:message_id>/', manager_views.manager_edit_message, name='manager_edit_message'),
    path('manager/clear_send_messages/', manager_views.clear_send_messages, name='clear_send_messages'),
    path('manager/project/create/', manager_views.manager_create_project, name='manager_create_project'),
    path('manager/project/manage/', manager_views.manager_manage_project, name='manager_manage_project'),
    path('manager/project/edit/<int:project_id>/', manager_views.manager_edit_project, name='manager_edit_project'),
    path('manager/project/delete/<int:project_id>/', manager_views.manager_delete_project, name='manager_delete_project'),
    path('manager/project/upload/<int:project_id>', manager_views.upload_file, name='upload_file'),
    path('manager/project/<int:project_id>/files/', manager_views.project_files, name='project_files'),
    path("manager/file/delete/<int:file_id>/", manager_views.manager_delete_file, name='manager_delete_file'),

    # # employer URL
    path("employer/home/", employer_views.employer_home, name='employer_home'),
    path("employer/view/profile/", employer_views.employer_view_profile,
         name='employer_view_profile'),
    path("employer/fcmtoken/", employer_views. employer_fcmtoken, name='employer_fcmtoken'),
    path("employer/view/notification/", employer_views.employer_view_notification,
         name="employer_view_notification"),
    path('employer/employer_receive_message/', employer_views.employer_receive_message, name='employer_receive_message'),
    path('employer/employer_send_message/', employer_views.employer_send_message, name='employer_send_message'),
    path('employer/employer_delete_send_message/<int:message_id>/', employer_views.employer_delete_send_message, name='employer_delete_send_message'),
    path('employer/employer_send_message/edit/<int:message_id>/', employer_views.employer_edit_message, name='employer_edit_message'),
    path('employer/employer_clear_send_messages/', employer_views.employer_clear_send_messages, name='employer_clear_send_messages'),
    path("employer/todolist/add/", employer_views.add_todolist_employer, name='add_todolist_employer'),
    path("employer/todolist/manage/", employer_views.manage_todolist_employer, name='manage_todolist_employer'),
    path("employer/todolist/delete/<int:todo_id>/", employer_views.delete_todolist_employer, name='delete_todolist_employer'),
    path("employer/todolist/update/<int:todo_id>/", employer_views.update_todolist_employer, name='update_todolist_employer'),
    path("employer/meeting/create/", employer_views.create_meeting_employer, name='create_meeting_employer'),
    path('employer/meeting/edit/<int:meeting_id>/', employer_views.edit_meeting_employer, name='edit_meeting_employer'),
    path("employer/meeting/delete/<int:meeting_id>/", employer_views.delete_meeting_employer, name='delete_meeting_employer'),
    path("employer/meeting/manage/", employer_views.manage_meeting_employer, name='manage_meeting_employer'),
    path('employer/meeting/filter_participants_employer/', employer_views.filter_participants_employer, name='filter_participants_employer'),
    path('employer/display_employer_meeting/', employer_views.display_employer_meeting, name='display_employer_meeting'),
    path('employer/update_employer_task/update/<int:task_id>/', employer_views.update_employer_task, name='update_employer_task'),
    path('employer/display_employer_tasks/', employer_views.display_employer_tasks, name='display_employer_tasks'),
    path('employer/project/display_projects_team/', employer_views.display_projects_team, name='display_projects_team'),
    path('employer/project/upload/<int:project_id>', employer_views.employer_upload_file, name='employer_upload_file'),
    path('employer/project/<int:project_id>/files/', employer_views.employer_project_files, name='employer_project_files'),
    path("employer/file/delete/<int:file_id>/", employer_views.employer_delete_file, name='employer_delete_file'),

]