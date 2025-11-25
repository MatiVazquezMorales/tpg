Feature: Notificación por carga semanal incompleta a gerente
  # US-004
  # Como gerente de operaciones
  # Quiero recibir una notificación si un empleado no cargo sus 40 horas semanales
  # Para saber en que se invirtieron las horas del empleado
  
  Scenario: Notificar al finalizar la semana sin completar 40 horas
    Given que es domingo a las 23:59
    And un empleado tiene registradas 32 horas semanales
    When se ejecuta la verificación semanal
    Then el sistema envía una notificación de un empleado que no cargo todas sus horas
