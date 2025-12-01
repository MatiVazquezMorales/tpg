Feature: Reporte de horas por empleado
  # US-005
  # Como gerente de operaciones
  # Quiero visualizar las horas cargadas por empleado y tarea
  # Para evaluar la productividad y cumplimiento de las 40 horas

  Scenario: Generar reporte semanal de un empleado
    Given que selecciono el período "semana actual"
    When genero el reporte
    Then el sistema muestra las horas cargadas por cada tarea y total semanal
