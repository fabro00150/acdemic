from django.shortcuts import render, get_object_or_404, redirect
from .models import Materia, Estudiante, Asistencia, Calificacion,Docente
from django.contrib import messages
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
    docentes = Docente.objects.all()
    materias = Materia.objects.all()

    # Procesar formulario de edición
    if request.method == "POST":
        docente_id = request.POST.get("docente_id")
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        email = request.POST.get("email")

        if docente_id:  # Actualizar docente
            docente = get_object_or_404(Docente, id=docente_id)
            docente.nombre = nombre
            docente.apellido = apellido
            docente.email = email
            docente.save()
            messages.success(request, "Docente actualizado correctamente.")
        else:  # Agregar nuevo docente
            Docente.objects.create(nombre=nombre, apellido=apellido, email=email)
            messages.success(request, "Docente agregado exitosamente.")

        return redirect("dcnts")

    return render(request, "agregar_docente.html", {"docentes": docentes, "materias": materias})

def dcnts(request):    
    docentes = Docente.objects.all()
    return render(request, "agregar_docentes", {"docentes": docentes})


def eliminar_docente(request, docente_id):
    docente = get_object_or_404(Docente, id=docente_id)
    docente.delete()
    messages.success(request, "Docente eliminado correctamente.")
    return redirect("inicio")


# Agregar materia
def agregar_materia(request):
    materias = Materia.objects.all()
    docentes = Docente.objects.all()
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        codigo = request.POST.get("codigo")
        docentes_ids = request.POST.getlist("docentes")  # Obtener IDs de los docentes seleccionados
        materia = Materia.objects.create(nombre=nombre, codigo=codigo)  # Crear materia
        materia.docentes.set(docentes_ids)  # Asociar docentes seleccionados a la materia
        return redirect("inicio")
    return render(request, "agregar_materia.html", {"materias": materias,"docentes":docentes})

def agregar_editar_materia(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        codigo = request.POST.get("codigo")
        docentes_ids = request.POST.getlist("docentes")  # Obtener IDs de los docentes seleccionados
        
        if "materia_id" in request.POST:  # Si se recibe un ID, actualizar la materia
            materia_id = request.POST.get("materia_id")
            materia = Materia.objects.get(id=materia_id)
            materia.nombre = nombre
            materia.codigo = codigo
            materia.docentes.set(docentes_ids)
            materia.save()
            return JsonResponse({"status": "success", "message": "Materia actualizada correctamente"})
        else:  # Si no hay ID, crear una nueva materia
            materia = Materia.objects.create(nombre=nombre, codigo=codigo)
            materia.docentes.set(docentes_ids)
            return JsonResponse({"status": "success", "message": "Materia creada correctamente"})
    return JsonResponse({"status": "error", "message": "Método no permitido"})

# Añadir estudiante
def agregar_estudiante(request):
    estudiantes = Estudiante.objects.all()  # Obtener todos los estudiantes
    materias = Materia.objects.all()  # Obtener todas las materias

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        matricula = request.POST.get("matricula")
        materias_ids = request.POST.getlist("materias")

        if nombre and apellido and matricula:  # Validar que los campos no estén vacíos
            estudiante = Estudiante.objects.create(
                nombre=nombre, apellido=apellido, matricula=matricula
            )
            estudiante.materias.set(materias_ids)
            return redirect("inicio")

    return render(
        request,
        "agregar_estudiante.html",
        {"materias": materias, "estudiantes": estudiantes},
    )

def agregar_editar_estudiante(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        matricula = request.POST.get("matricula")
        materias_ids = request.POST.getlist("materias")  # Obtener IDs de las materias seleccionadas

        if "estudiante_id" in request.POST:  # Si se recibe un ID, actualizar el estudiante
            estudiante_id = request.POST.get("estudiante_id")
            estudiante = Estudiante.objects.get(id=estudiante_id)
            estudiante.nombre = nombre
            estudiante.apellido = apellido
            estudiante.matricula = matricula
            estudiante.materias.set(materias_ids)
            estudiante.save()
            return JsonResponse({"status": "success", "message": "Estudiante actualizado correctamente"})
        else:  # Si no hay ID, crear un nuevo estudiante
            estudiante = Estudiante.objects.create(nombre=nombre, apellido=apellido, matricula=matricula)
            estudiante.materias.set(materias_ids)
            return JsonResponse({"status": "success", "message": "Estudiante creado correctamente"})
    return JsonResponse({"status": "error", "message": "Método no permitido"})