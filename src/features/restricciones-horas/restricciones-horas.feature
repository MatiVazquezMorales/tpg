Feature: Restricciones de tiempo y formato en carga de horas
  # US-002
  # Como empleado
  # Quiero que se validen las horas que registro
  # Para cumplir con las políticas internas

  Scenario: Intentar cargar más de 24 horas en un día
    Given que ingreso 25 horas en un mismo día
    When intento guardar la carga
    Then el sistema muestra el mensaje "No se pueden registrar más de 24 horas por día"

  Scenario: Intentar cargar horas en fechas futuras
    Given que selecciono una fecha posterior al día actual
    When intento registrar horas
    Then el sistema muestra el mensaje "No se pueden cargar horas de fechas futuras"
