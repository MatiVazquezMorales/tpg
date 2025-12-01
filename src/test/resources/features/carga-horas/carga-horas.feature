Feature: Carga de horas en tareas abiertas
  # US-001
  # Como empleado
  # Quiero registrar mis horas trabajadas en tareas
  # Para reflejar mi dedicación semanal y cumplir con las 40 horas requeridas

  Scenario: Registrar horas en una tarea activa
    Given que estoy asignado a una tarea con estado "abierta"
    When ingreso 4 horas trabajadas para el día martes
    Then el sistema registra correctamente las horas

  Scenario: Intentar registrar horas en una tarea cerrada
    Given que la tarea tiene estado "cerrada"
    When intento ingresar horas
    Then el sistema muestra un mensaje "No se pueden cargar horas en tareas cerradas"


#  Scenario: Bloquear carga en tareas no iniciadas
#    Given una tarea con estado "no iniciada"
#    When el usuario intenta registrar 2 horas
#    Then el sistema muestra el mensaje "No puede registrar horas en tareas no iniciadas"


