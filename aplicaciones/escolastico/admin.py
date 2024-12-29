from django.contrib import admin
from .models import  Estudiante,Asistencia,Calificacion
# Register your models here.

admin.site.register(Estudiante)
admin.site.register(Asistencia)
admin.site.register(Calificacion)