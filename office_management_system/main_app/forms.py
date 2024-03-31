from django import forms
from django.forms.widgets import DateInput, TextInput

from .models import *


class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # Here make some changes such as:
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


class CustomUserForm(FormSettings):
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')])
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    job_title = forms.CharField(required=True)
    address = forms.CharField(widget=forms.Textarea)
    password = forms.CharField(widget=forms.PasswordInput)
    widget = {
        'password': forms.PasswordInput(),
    }
    profile_pic = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)

        if kwargs.get('instance'):
            instance = kwargs.get('instance').admin.__dict__
            self.fields['password'].required = False
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"

    def clean_email(self, *args, **kwargs):
        formEmail = self.cleaned_data['email'].lower()
        if self.instance.pk is None:  # Insert
            if CustomUser.objects.filter(email=formEmail).exists():
                raise forms.ValidationError(
                    "The given email is already registered")
        else:  # Update
            dbEmail = self.Meta.model.objects.get(
                id=self.instance.pk).admin.email.lower()
            if dbEmail != formEmail:  # There has been changes
                if CustomUser.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError("The given email is already registered")

        return formEmail

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'gender', 'job_title', 'password', 'profile_pic', 'address']


class AdminForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Admin
        fields = CustomUserForm.Meta.fields


class EmployerForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(EmployerForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Employer
        fields = CustomUserForm.Meta.fields + \
                 ['department']


class ManagerForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(ManagerForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Manager
        fields = CustomUserForm.Meta.fields + \
                 ['department']


class DepartmentForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(DepartmentForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['name', 'description']
        model = Department


class ToDoListForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(ToDoListForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['name', 'description', 'due_time', 'due_date']
        model = TodoList
        widgets = {
            'due_time': forms.DateInput(attrs={'type': 'time'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class MeetingForm(FormSettings):
    participants = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(user_type__in=[2, 3]),  # Update to include all users initially
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Meeting
        fields = ['title', 'description', 'time', 'date', 'participants']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        meeting_instance = kwargs.pop('meeting_instance', None)  # Get meeting instance if provided
        super(MeetingForm, self).__init__(*args, **kwargs)
        if meeting_instance:
            # If a meeting instance is provided, set the queryset for participants accordingly
            self.fields['participants'].queryset = meeting_instance.participants.all()


class FilterParticipantsForm(forms.Form):
    USER_CHOICES = (
        ('2', 'Manager'),
        ('3', 'Employer'),
    )

    user_type = forms.ChoiceField(choices=USER_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    department = forms.ModelChoiceField(queryset=Department.objects.all(),
                                        widget=forms.Select(attrs={'class': 'form-control'}), required=False)


class TaskForm(FormSettings):
    def __init__(self, *args, **kwargs):
        user_type = kwargs.pop('user_type', None)
        try:
            manager_department = kwargs.pop('manager_department')
        except KeyError:
            manager_department = None

        super(TaskForm, self).__init__(*args, **kwargs)

        if user_type == '2' and manager_department:
            # Filter user choices to only show employees (user_type 3) in the same department as the manager
            self.fields['user'].queryset = CustomUser.objects.filter(user_type='3',
                                                                     employer__department=manager_department)
        elif user_type == '1':
            # Show all managers and employers for admin
            self.fields['user'].queryset = CustomUser.objects.filter(user_type__in=['2', '3'])

    def save(self, commit=True, user=None):
        task = super(TaskForm, self).save(commit=False)
        if user:
            task.manager = user
        if commit:
            task.save()
        return task

    class Meta:
        model = Task
        fields = ['user', 'title', 'description', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ManagerEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(ManagerEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Manager
        fields = CustomUserForm.Meta.fields


class MessageForm(FormSettings):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Retrieve the user from kwargs
        super(MessageForm, self).__init__(*args, **kwargs)
        if user:
            # Exclude the current user from the receiver choices
            self.fields['receiver'].queryset = self.fields['receiver'].queryset.exclude(id=user.id)

    class Meta:
        model = Message
        fields = ['receiver', 'message']


class ProjectForm(FormSettings):
    manager_department = None

    def __init__(self, *args, **kwargs):
        self.manager_department = kwargs.pop('manager_department', None)
        super(ProjectForm, self).__init__(*args, **kwargs)

        if self.manager_department:
            # Filter Project_team choices to only show employers in the same department as the manager
            self.fields['Project_team'].queryset = Employer.objects.filter(department=self.manager_department)

    def save(self, commit=True, user=None):
        project = super(ProjectForm, self).save(commit=False)
        if user:
            project.project_manager = user
        if commit:
            project.save()  # Save the project first to get an ID for ManyToMany relationship
            project.Project_team.set(self.cleaned_data['Project_team'])  # Save the ManyToMany relationship
        return project

    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'Project_team']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'Project_team': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class FileUploadForm(FormSettings):
    class Meta:
        model = File
        fields = ['name', 'file']


class EmployerEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(EmployerEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Employer
        fields = CustomUserForm.Meta.fields
