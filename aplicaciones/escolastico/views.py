from django.shortcuts import render, get_object_or_404, redirect
from .models import Materia, Estudiante, Asistencia, Calificacion,Docente
from django.contrib import messages
from django.http import JsonResponse


def inicio(request):
    """Página inicial que muestra las materias disponibles."""
    materias = Materia.objects.all()
    return render(request, 'inicio.html', {'materias': materias})

def home(request):
    """Página inicial que muestra las materias disponibles."""
    materias = Materia.objects.all()
    return render(request, 'home.html', {'materias': materias})


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

#INGRESAR CALIFICACIONES
def ingresar_calificaciones(request, materia_id):
    """Vista para ingresar calificaciones de estudiantes."""
    materia = get_object_or_404(Materia, id=materia_id)
    estudiantes = materia.estudiantes.all()

    estudiantes_calificaciones = []
    for estudiante in estudiantes:
        calificaciones = Calificacion.objects.filter(estudiante=estudiante, materia=materia).order_by('parcial')
        calificaciones_dict = {calificacion.parcial: calificacion.nota for calificacion in calificaciones}
        estudiantes_calificaciones.append({
            'id': estudiante.id,
            'nombre': estudiante.nombre,
            'apellido': estudiante.apellido,
            'calificaciones': calificaciones_dict,
        })

    if request.method == 'POST':
        for estudiante in estudiantes:
            for parcial in range(1, 4):  # Se asume hasta 3 parciales
                nota = request.POST.get(f'calificacion_{estudiante.id}_{parcial}')
                if nota:
                    Calificacion.objects.update_or_create(
                        estudiante=estudiante,
                        materia=materia,
                        parcial=parcial,
                        defaults={'nota': float(nota)}
                    )
        return JsonResponse({'success': True, 'message': 'Calificaciones registradas con éxito'})

    return render(request, 'ingresar_calificaciones.html', {
        'materia': materia,
        'estudiantes': estudiantes_calificaciones,
        'parciales_rango': range(1, 4),
    })

def obtener_calificaciones(request, estudiante_id, parcial):
    calificaciones = Calificacion.objects.filter(estudiante_id=estudiante_id, parcial=parcial).values_list('nota', flat=True)
    notas = list(calificaciones) + [0] * (5 - len(calificaciones))  # Rellenar con ceros si hay menos de 5 notas
    return JsonResponse({'notas': notas})

#REPORTES DE MATERIA
def generar_reportes(request, materia_id):
    """Vista para generar reportes con totales de asistencias, faltas, y promedios de calificaciones."""
    materia = get_object_or_404(Materia, id=materia_id)
    estudiantes = materia.estudiantes.all()
    asistencia = Asistencia.objects.filter(materia=materia)
    calificaciones = Calificacion.objects.filter(materia=materia)

    datos = []
    for estudiante in estudiantes:
        asistencias_estudiante = asistencia.filter(estudiante=estudiante, presente=True)
        faltas_estudiante = asistencia.filter(estudiante=estudiante, presente=False)
        calificaciones_estudiante = calificaciones.filter(estudiante=estudiante).order_by('-id')[:5]  # Últimas 5 notas
        promedio = (
            sum(calificacion.nota for calificacion in calificaciones_estudiante) / calificaciones_estudiante.count()
            if calificaciones_estudiante.exists() else 0
        )

        datos.append({
            'estudiante': estudiante,
            'total_asistencias': asistencias_estudiante.count(),
            'total_faltas': faltas_estudiante.count(),
            'asistencias': [a.fecha for a in asistencias_estudiante],
            'faltas': [f.fecha for f in faltas_estudiante],
            'calificaciones': calificaciones_estudiante,
            'promedio': promedio,
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

        return render(request,"agregar_docente.html", {"docentes": docentes, "materias": materias})

    return render(request, "agregar_docente.html", {"docentes": docentes, "materias": materias})

def eliminar_docente(request, docente_id):
    docentes = Docente.objects.all()
    materias = Materia.objects.all()
    docente = get_object_or_404(Docente, id=docente_id)
    docente.delete()
    messages.success(request, "Docente eliminado correctamente.")
    return render(request,"agregar_docente.html", {"docentes": docentes, "materias": materias})

def eliminarEstudiante(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    estudiante.delete()
    messages.success(request, "Estudiante eliminado correctamente.")
    return redirect("home")

def eliminarMateria(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)
    materia.delete()
    messages.success(request, "materia eliminado correctamente.")
    return redirect("home")

# Agregar materia
def agregar_materia(request):
    materias = Materia.objects.all().prefetch_related('docentes', 'estudiantes')
    docentes = Docente.objects.all()

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        codigo = request.POST.get("codigo", "").strip()
        docentes_ids = request.POST.getlist("docentes")  # Obtener IDs de los docentes seleccionados

        # Validar campos obligatorios
        if not nombre or not codigo:
            return render(request, "agregar_materia.html", {
                "materias": materias,
                "docentes": docentes,
                "error": "Todos los campos son obligatorios."
            })

        try:
            materia = Materia.objects.create(nombre=nombre, codigo=codigo)
            materia.docentes.set(docentes_ids)
            return redirect("home")  # Redirigir a la página principal o donde prefieras
        except Exception as e:
            return render(request, "agregar_materia.html", {
                "materias": materias,
                "docentes": docentes,
                "error": f"Error al guardar la materia: {str(e)}"
            })

    return render(request, "agregar_materia.html", {"materias": materias, "docentes": docentes})

def agregar_editar_materia(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        codigo = request.POST.get("codigo", "").strip()
        docentes_ids = request.POST.getlist("docentes")

        # Validar campos obligatorios
        if not nombre or not codigo:
            return JsonResponse({"status": "error", "message": "Todos los campos son obligatorios"})

        materia_id = request.POST.get("materia_id", "").strip()

        try:
            if materia_id:  # Si se recibe un ID, actualizar la materia
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
        except Materia.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Materia no encontrada"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Error al procesar la materia: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Método no permitido"})

# Añadir estudiante
def agregar_estudiante(request):
    estudiantes = Estudiante.objects.all()  # Obtener todos los estudiantes
    materias = Materia.objects.all()  # Obtener todas las materias

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        apellido = request.POST.get("apellido", "").strip()
        matricula = request.POST.get("matricula", "").strip()
        materias_ids = request.POST.getlist("materias")

        # Validar campos obligatorios
        if not nombre or not apellido or not matricula:
            return render(request, "agregar_estudiante.html", {
                "materias": materias,
                "estudiantes": estudiantes,
                "error": "Todos los campos son obligatorios."
            })

        try:
            estudiante = Estudiante.objects.create(
                nombre=nombre, apellido=apellido, matricula=matricula
            )
            estudiante.materias.set(materias_ids)
            return redirect("home")
        except Exception as e:
            return render(request, "agregar_estudiante.html", {
                "materias": materias,
                "estudiantes": estudiantes,
                "error": f"Error al guardar: {str(e)}"
            })

    return render(request, "agregar_estudiante.html", {
        "materias": materias,
        "estudiantes": estudiantes
    })

def agregar_editar_estudiante(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        apellido = request.POST.get("apellido", "").strip()
        matricula = request.POST.get("matricula", "").strip()
        materias_ids = request.POST.getlist("materias")

        # Validar campos obligatorios
        if not nombre or not apellido or not matricula:
            return JsonResponse({"status": "error", "message": "Todos los campos son obligatorios"})

        estudiante_id = request.POST.get("estudiante_id", "").strip()

        if estudiante_id:  # Actualizar estudiante existente
            try:
                estudiante = Estudiante.objects.get(id=estudiante_id)
                estudiante.nombre = nombre
                estudiante.apellido = apellido
                estudiante.matricula = matricula
                estudiante.materias.set(materias_ids)
                estudiante.save()
                return JsonResponse({"status": "success", "message": "Estudiante actualizado correctamente"})
            except Estudiante.DoesNotExist:
                return JsonResponse({"status": "error", "message": "Estudiante no encontrado"})
            except Exception as e:
                return JsonResponse({"status": "error", "message": f"Error al actualizar: {str(e)}"})
        else:  # Crear nuevo estudiante
            try:
                estudiante = Estudiante.objects.create(
                    nombre=nombre, apellido=apellido, matricula=matricula
                )
                estudiante.materias.set(materias_ids)
                return JsonResponse({"status": "success", "message": "Estudiante creado correctamente"})
            except Exception as e:
                return JsonResponse({"status": "error", "message": f"Error al crear: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Método no permitido"})

def borrar_calificaciones(request, estudiante_id):
    if request.method == 'POST':
        estudiante = get_object_or_404(Estudiante, id=estudiante_id)
        Calificacion.objects.filter(estudiante=estudiante).delete()
        return JsonResponse({'success': True, 'message': 'Calificaciones borradas con éxito'})
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

from django.db.models import Avg
def generar_reporte_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    materias = estudiante.materias.all()
    asistencias = Asistencia.objects.filter(estudiante=estudiante)
    calificaciones = Calificacion.objects.filter(estudiante=estudiante).order_by('materia', 'parcial')

    datos_materias = []
    suma_promedios = 0
    total_materias = materias.count()

    for materia in materias:
        calificaciones_materia = calificaciones.filter(materia=materia)
        promedio = calificaciones_materia.aggregate(promedio=Avg('nota'))['promedio'] or 0
        suma_promedios += promedio
        total_faltas = asistencias.filter(materia=materia, presente=False).count()
        porcentaje_asistencia = 100 * asistencias.filter(materia=materia, presente=True).count() / asistencias.filter(materia=materia).count() if asistencias.filter(materia=materia).count() > 0 else 0
        
        # Completar con celdas vacías
        calificaciones_list = list(calificaciones_materia)
        while len(calificaciones_list) < 3:
            calificaciones_list.append(None)
        
        datos_materias.append({
            'codigo': materia.codigo,
            'materia': materia.nombre,
            'calificaciones': calificaciones_list,
            'promedio': promedio,
            'total_faltas': total_faltas,
            'porcentaje_asistencia': porcentaje_asistencia
        })

    promedio_general = suma_promedios / total_materias if total_materias > 0 else 0

    context = {
        'estudiante': estudiante,
        'materias': datos_materias,
        'asistencias': asistencias,
        'suma_promedios': suma_promedios,
        'promedio_general': promedio_general,
    }
    return render(request, 'reporte.html', context)
