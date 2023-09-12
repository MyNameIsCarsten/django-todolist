from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Task

class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('tasks')

class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save() # once form is saved, the return value will be user
        if user is not None: # user was successfully created
            login(self.request, user) # login created user directly
        return super(RegisterPage, self).form_valid(form)
    
    # don't show loged in user the register page
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect ('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks' # default is object_list

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # context['tasks'] is the full queryset
        context['tasks'] = context['tasks'].filter(user=self.request.user) # only show user specifc tasks
        context['count'] = context['tasks'].filter(complete=False) # Count of incomplete items

        # Search
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            # icontains -> contains | startswith --> starts with
            context['tasks'] = context['tasks'].filter(title__icontains=search_input)

        context['search_input'] = search_input # pass in search_input into our form so that user sees what he was searching
        return context

class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task' # default is object_list
    template_name = 'base/task.html' # default is task_detail.html

class TaskCreate (LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form): # being triggered by default on post request
        form.instance.user = self.request.user # assign current user to the form field 'user'
        return super (TaskCreate, self).form_valid(form)

class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task' # default is object_list
    success_url = reverse_lazy('tasks')