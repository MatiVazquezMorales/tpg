package steps;

import domain.EstadoTarea;
import domain.Tarea;
import domain.TareaRepository;
import service.carga.ServicioCargaHoras;

import io.cucumber.java.es.*;
import static org.junit.jupiter.api.Assertions.*;
import java.time.LocalDate;

public class CargaHorasSteps {

    private final TareaRepository repository = TestContext.getRepository();
    private final ServicioCargaHoras servicio = new ServicioCargaHoras(repository);

    private Exception excepcion;
    private Tarea tarea;


    @Dado("que estoy asignado a una tarea con estado {string}")
    public void que_estoy_asignado_a_una_tarea_con_estado(String estado) {
        TestContext.reset();
        EstadoTarea est = EstadoTarea.valueOf(estado.replace(" ", "").toUpperCase());
        tarea = new Tarea("Tarea1", est);
        repository.guardar(tarea);
    }

    @Dado("que la tarea tiene estado {string}")
    public void que_la_tarea_tiene_estado(String estado) {
        TestContext.reset();
        EstadoTarea est = EstadoTarea.valueOf(estado.replace(" ", "").toUpperCase());
        tarea = new Tarea("TareaCerrada", est);
        repository.guardar(tarea);
    }


    @Cuando("ingreso {int} horas trabajadas para el día martes")
    public void ingreso_horas_trabajadas_para_el_dia_martes(Integer horas) {
        excepcion = null;
        try {
            servicio.cargarHoras(tarea.getNombre(),
                    LocalDate.now().with(java.time.DayOfWeek.TUESDAY),
                    horas);
        } catch (Exception e) {
            excepcion = e;
        }
    }

    @Cuando("intento ingresar horas")
    public void intento_ingresar_horas() {
        excepcion = null;
        try {
            servicio.cargarHoras(tarea.getNombre(), LocalDate.now(), 3);
        } catch (Exception e) {
            excepcion = e;
        }
    }


    @Entonces("el sistema registra correctamente las horas")
    public void el_sistema_registra_correctamente_las_horas() {
        assertNull(excepcion, "No debería haber excepción");
        assertEquals(1, tarea.getHoras().size());
    }

    @Entonces("el sistema muestra un mensaje {string}")
    public void el_sistema_muestra_un_mensaje(String mensajeEsperado) {
        assertNotNull(excepcion, "Se esperaba una excepción, pero no se lanzó ninguna");
        assertEquals(mensajeEsperado, excepcion.getMessage());
    }
}
