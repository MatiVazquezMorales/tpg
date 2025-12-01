package steps;

import domain.*;
import service.carga.ServicioCargaHoras;

import io.cucumber.java.es.*;
import static org.junit.jupiter.api.Assertions.*;

import java.time.LocalDate;
import java.time.temporal.WeekFields;
import java.util.*;

public class ReporteHorasSteps {

    private final TareaRepository repository = TestContext.getRepository();
    private final ServicioCargaHoras cargaHorasService = new ServicioCargaHoras(repository);

    private LocalDate fechaInicioSemana;
    private LocalDate fechaFinSemana;
    private Map<String, Object> reporteGenerado;


    @Dado("que selecciono el período {string}")
    public void que_selecciono_el_periodo(String periodo) {
        TestContext.reset();
        if (periodo.equalsIgnoreCase("semana actual")) {
            WeekFields wf = WeekFields.of(Locale.getDefault());
            LocalDate hoy = LocalDate.now();

            fechaInicioSemana = hoy.with(wf.dayOfWeek(), 1);
            fechaFinSemana    = hoy.with(wf.dayOfWeek(), 7);

            Tarea backend = new Tarea("Backend", EstadoTarea.ABIERTA);
            Tarea frontend = new Tarea("Frontend", EstadoTarea.ABIERTA);

            repository.guardar(backend);
            repository.guardar(frontend);

            // Cargar horas en fechas pasadas dentro de la semana actual
            // Usar siempre fechas que estén en el pasado o hoy, dentro de la semana
            LocalDate fecha1 = hoy.minusDays(2);
            LocalDate fecha2 = hoy.minusDays(1);
            LocalDate fecha3 = hoy;
            
            // Asegurar que las fechas estén dentro de la semana actual
            if (fecha1.isBefore(fechaInicioSemana)) {
                fecha1 = fechaInicioSemana;
            }
            if (fecha2.isBefore(fechaInicioSemana)) {
                fecha2 = fechaInicioSemana.plusDays(1);
            }
            if (fecha3.isBefore(fechaInicioSemana)) {
                fecha3 = fechaInicioSemana.plusDays(2);
            }
            
            // Asegurar que no sean futuras (aunque ya deberían estar bien)
            if (fecha1.isAfter(hoy)) {
                fecha1 = hoy;
            }
            if (fecha2.isAfter(hoy)) {
                fecha2 = hoy;
            }
            if (fecha3.isAfter(hoy)) {
                fecha3 = hoy;
            }

            cargaHorasService.cargarHoras("Backend", fecha1, 4);
            cargaHorasService.cargarHoras("Backend", fecha2, 6);
            cargaHorasService.cargarHoras("Frontend", fecha3, 5);
        }
    }


    @Cuando("genero el reporte")
    public void genero_el_reporte() {
        Map<String, Integer> horasPorTarea = new HashMap<>();
        int totalSemanal = 0;

        for (Tarea tarea : repository.buscarTodos()) {
            int totalTarea = tarea.getHoras().stream()
                    .filter(h -> !h.getFecha().isBefore(fechaInicioSemana)
                            && !h.getFecha().isAfter(fechaFinSemana))
                    .mapToInt(HorasCargadas::getHoras)
                    .sum();

            if (totalTarea > 0) {
                horasPorTarea.put(tarea.getNombre(), totalTarea);
                totalSemanal += totalTarea;
            }
        }

        reporteGenerado = Map.of(
                "detalle", horasPorTarea,
                "totalSemanal", totalSemanal
        );
    }


    @Entonces("el sistema muestra las horas cargadas por cada tarea y total semanal")
    public void el_sistema_muestra_las_horas_cargadas_por_cada_tarea_y_total_semanal() {
        assertNotNull(reporteGenerado, "Debe generarse un reporte");

        Map<String, Integer> detalle = (Map<String, Integer>) reporteGenerado.get("detalle");
        int total = (int) reporteGenerado.get("totalSemanal");

        assertFalse(detalle.isEmpty(), "Debe mostrar horas por tarea");
        assertTrue(total > 0, "El total semanal debe ser mayor a 0");

        assertEquals(10, (int) detalle.get("Backend"));
        assertEquals(5, (int) detalle.get("Frontend"));
        assertEquals(15, total);
    }
}
