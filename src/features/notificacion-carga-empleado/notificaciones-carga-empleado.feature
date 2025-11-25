Feature: Notificación por carga semanal incompleta a empleado
  # US-003
  # Como empleado
  # Quiero recibir una notificación si no cargo mis 40 horas semanales
  # Para completar la carga antes del cierre

  Scenario: Notificar al finalizar la semana sin completar 40 horas
    Given que es domingo a las 23:59
    And tengo registradas 32 horas semanales
    When se ejecuta la verificación semanal
    Then el sistema envía una notificación recordando completar las horas restantes
