from django.db import models

class Docente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Materia(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True)
    docentes = models.ManyToManyField('Docente', related_name="materias")

    def __str__(self):
        return self.nombre


class Estudiante(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    matricula = models.CharField(max_length=10, unique=True)
    materias = models.ManyToManyField(Materia, related_name="estudiantes")

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Asistencia(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name="asistencias")
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name="asistencias")
    fecha = models.DateField()
    presente = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.estudiante} - {self.materia} ({self.fecha})"

class Calificacion(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name="calificaciones")
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name="calificaciones")
    parcial = models.PositiveIntegerField()  # Añadir el campo de parcial
    nota = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.estudiante} - {self.materia} - Parcial {self.parcial}: {self.nota}"
