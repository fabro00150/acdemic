from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('marcar_asistencia/<int:materia_id>', views.marcar_asistencia),
    path('ingresar_calificaciones/<int:materia_id>', views.ingresar_calificaciones),
    path('generar_reportes/<int:materia_id>', views.generar_reportes),
    
     path("agregar_docente/", views.agregar_docente),
    path("agregar_materia/", views.agregar_materia),
    path("agregar_estudiante/", views.agregar_estudiante),
]
