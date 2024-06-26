from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import redirect


class LoginCheckMiddleWare(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user  # Who is the current user?

        if user.is_authenticated:
            if user.user_type == '1':  # Is it the HOD/Admin?
                if modulename == 'main_app.employer_views':
                    return redirect(reverse('admin_home'))
            elif user.user_type == '2':  # Staff or Manager?
                if modulename == 'main_app.employer_views' or modulename == 'main_app.hod_views':
                    return redirect(reverse('manager_home'))
            elif user.user_type == '3':  # Employer or Student?
                if modulename == 'main_app.hod_views' or modulename == 'main_app.manager_views':
                    return redirect(reverse('employer_home'))
            else:  # None of the above? Take the user to the login page.
                return redirect(reverse('login_page'))
        else:
            if request.path == reverse(
                    'login_page') or modulename == 'django.contrib.auth.views' or request.path == reverse('user_login'):
                pass  # If the path is login or has anything to do with authentication, pass
            else:
                return redirect(reverse('login_page'))
