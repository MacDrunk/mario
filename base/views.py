from django.urls import reverse

from django.shortcuts import render, redirect
from django.template.context_processors import request
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView,UpdateView,DeleteView,FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView,LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Tarea
from django.contrib import auth


# Create your views here.
class ListaPendientes(LoginRequiredMixin,ListView):
    model = Tarea
    context_object_name = 'tareas'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tareas'] = context['tareas'].filter(usuario=self.request.user)
        context['count'] = context['tareas'].filter(completo=False).count()

        valor_buscar = self.request.GET.get('buscar-texto' or'')
        if valor_buscar:
            context['tareas'] = context['tareas'].filter(titulo__icontains=valor_buscar)
        context['valor_buscar'] = valor_buscar
        return context

class DetalleTarea(LoginRequiredMixin,DetailView):
    model = Tarea
    context_object_name = 'tarea'
    template_name = 'base/Tarea.html' # Corrected Tarea.html

    def get_queryset(self):
        base_qs = super().get_queryset()
        return base_qs.filter(usuario=self.request.user)

class CrearTarea(LoginRequiredMixin,CreateView):
    model = Tarea
    fields = ['titulo','descripccion','completo']
    success_url = reverse_lazy('tarea')

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super(CrearTarea,self).form_valid(form)

class EditarTarea(LoginRequiredMixin,UpdateView):
    model = Tarea
    fields = ['titulo','descripccion','completo']
    success_url = reverse_lazy('tarea')

    def get_queryset(self):
        base_qs = super().get_queryset()
        return base_qs.filter(usuario=self.request.user)

class Eliminartarea(LoginRequiredMixin,DeleteView):
    model = Tarea
    context_object_name = 'tarea'
    success_url = reverse_lazy('tarea')

    def get_queryset(self):
        base_qs = super().get_queryset()
        return base_qs.filter(usuario=self.request.user)

class Logueo(LoginView):
    template_name = 'base/login.html'
    field = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tarea')

def Logout(request):
    auth.logout(request)
    return redirect('login')

class PaginaRegistro(FormView):
    template_name = 'base/Registro.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tarea')

    def form_valid(self, form):
        usuario = form.save()
        if usuario is not None:
            login(self.request,usuario)
        return super(PaginaRegistro,self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tarea')
        return super(PaginaRegistro,self).get(*args,**kwargs)