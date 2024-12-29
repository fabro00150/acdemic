from django.shortcuts import render, get_object_or_404, redirect
from .models import Materia, Estudiante, Asistencia, Calificacion,Docente

from django.http import JsonResponse

def inicio(request):
    """Página inicial que muestra las materias disponibles."""
    materias = Materia.objects.all()
    return render(request, 'inicio.html', {'materias': materias})

def marcar_asistencia(request, materia_id):
    """Vista para marcar la asistencia de estudiantes de una materia."""
    materia = get_object_or_404(Materia, id=materia_id)
    estudiantes = materia.estudiantes.all()

    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        for estudiante in estudiantes:
            presente = request.POST.get(f'asistencia_{estudiante.id}') == 'on'
            
            Asistencia.objects.create(
                estudiante=estudiante,
                materia=materia,
                fecha=fecha,
                presente=presente
            )
        return JsonResponse({'success': True, 'message': 'Asistencia registrada con éxito'})

    
    return render(request, 'marcar_asistencia.html', {'materia': materia, 'estudiantes': estudiantes})

def ingresar_calificaciones(request, materia_id):
    """Vista para ingresar calificaciones de estudiantes."""
    materia = get_object_or_404(Materia, id=materia_id)
    estudiantes = materia.estudiantes.all()

    if request.method == 'POST':
        for estudiante in estudiantes:
            nota = request.POST.get(f'calificacion_{estudiante.id}')
            if nota:
                Calificacion.objects.update_or_create(
                    estudiante=estudiante,
                    materia=materia,
                    defaults={'nota': nota}
                )
        return JsonResponse({'success': True, 'message': 'Calificaciones registradas con éxito'})

    return render(request, 'ingresar_calificaciones.html', {'materia': materia, 'estudiantes': estudiantes})

def generar_reportes(request, materia_id):
    """Vista para generar reportes de progreso por estudiante."""
    materia = get_object_or_404(Materia, id=materia_id)
    estudiantes = materia.estudiantes.all()
    asistencia = Asistencia.objects.filter(materia=materia)
    calificaciones = Calificacion.objects.filter(materia=materia)

    datos = []
    for estudiante in estudiantes:
        asistencias_estudiante = asistencia.filter(estudiante=estudiante)
        calificaciones_estudiante = calificaciones.filter(estudiante=estudiante)
        datos.append({
            'estudiante': estudiante,
            'asistencias': asistencias_estudiante,
            'calificaciones': calificaciones_estudiante,
        })

    return render(request, 'generar_reportes.html', {'materia': materia, 'datos': datos})

def agregar_docente(request):
    materias = Materia.objects.all()
    docentes = Docente.objects.all()
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        email = request.POST.get("email")

        if not nombre or not apellido or not email:
            return render(request, "agregar_docente.html", {
                "error": "Todos los campos son obligatorios."
            })

        # Crear el docente
        Docente.objects.create(nombre=nombre, apellido=apellido, email=email)
        return redirect("inicio")

    return render(request, "agregar_docente.html",{"materias": materias,"docentes":docentes})

# Agregar materia
def agregar_materia(request):
    docentes = Docente.objects.all()
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        codigo = request.POST.get("codigo")
        docentes_ids = request.POST.getlist("docentes")  # Obtener IDs de los docentes seleccionados
        materia = Materia.objects.create(nombre=nombre, codigo=codigo)  # Crear materia
        materia.docentes.set(docentes_ids)  # Asociar docentes seleccionados a la materia
        return redirect("inicio")
    return render(request, "agregar_materia.html", {"docentes": docentes})

# Añadir estudiante
def agregar_estudiante(request):
    materias = Materia.objects.all()
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        matricula = request.POST.get("matricula")
        materias_ids = request.POST.getlist("materias")
        estudiante = Estudiante.objects.create(nombre=nombre, apellido=apellido, matricula=matricula)
        estudiante.materias.set(materias_ids)
        return redirect("inicio")
    return render(request, "agregar_estudiante.html", {"materias": materias})