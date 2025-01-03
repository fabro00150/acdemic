from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('home/', views.home),
    path('marcar_asistencia/<int:materia_id>', views.marcar_asistencia),
    path('ingresar_calificaciones/<int:materia_id>', views.ingresar_calificaciones),
    path('obtener_calificaciones/<int:estudiante_id>/<int:parcial>', views.obtener_calificaciones), 
    path('generar_reportes/<int:materia_id>', views.generar_reportes),
    
    path("agregar_docente/", views.agregar_docente),
    path("agregar_materia/", views.agregar_materia),
    path("agregar_editar_materia/", views.agregar_editar_materia),
    path("agregar_estudiante/", views.agregar_estudiante),
    path("agregar_editar_estudiante/", views.agregar_editar_estudiante),
    path("eliminar_docente/<int:docente_id>", views.eliminar_docente),
    path("eliminarEstudiante/<int:estudiante_id>", views.eliminarEstudiante),
    path("eliminarMateria/<int:materia_id>", views.eliminarMateria),
    
    
      
    path("borrar_calificaciones/<int:estudiante_id>", views.borrar_calificaciones),    
    path('generar_reporte_estudiante/<int:estudiante_id>', views.generar_reporte_estudiante)
]
