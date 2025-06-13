from django.urls import path
from django.contrib.auth import views as auth_views, logout
from  django.contrib.auth.views import LogoutView
from tkinter.font import names
from django.urls import path
from .views import ( ListaPendientes, DetalleTarea, CrearTarea, EditarTarea,Eliminartarea,Logueo,PaginaRegistro
                     )
from . import views

urlpatterns=[path('',views.ListaPendientes.as_view(),name='tarea'),
             path('login/',Logueo.as_view(),name='login'),
             path('registro/',PaginaRegistro.as_view(),name='registro'),
             path('logout/',views.Logout,name='logout'),
             path('tarea/<int:pk>',DetalleTarea.as_view(),name='tarea'),
             path('crear-Tarea/',CrearTarea.as_view(),name='crear-tarea'),
             path('editar-tarea/<int:pk>',EditarTarea.as_view(),name='editar-tarea'),
             path('eliminar-tarea/<int:pk>',Eliminartarea.as_view(),name='eliminar-tarea')]