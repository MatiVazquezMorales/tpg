package steps;

import domain.*;
import service.carga.ServicioCargaHoras;

import io.cucumber.java.es.*;
import static org.junit.jupiter.api.Assertions.*;
import java.time.LocalDate;

public class RestriccionesSteps {

    private final TareaRepository repository = TestContext.getRepository();
    private final ServicioCargaHoras servicio = new ServicioCargaHoras(repository);

    private String nombreTarea;
    private LocalDate fechaSeleccionada;
    private int horasIngresadas;
    private Exception excepcion;


    @Dado("que ingreso {int} horas en un mismo día")
    public void que_ingreso_horas_en_un_mismo_dia(Integer horas) {
        TestContext.reset();
        nombreTarea = "TareaActiva";
        horasIngresadas = horas;
        fechaSeleccionada = LocalDate.now();

        Tarea tarea = new Tarea(nombreTarea, EstadoTarea.ABIERTA);
        repository.guardar(tarea);
    }

    @Dado("que selecciono una fecha posterior al día actual")
    public void que_selecciono_una_fecha_posterior_al_dia_actual() {
        TestContext.reset();
        nombreTarea = "TareaActiva";
        horasIngresadas = 5;
        fechaSeleccionada = LocalDate.now().plusDays(2);

        Tarea tarea = new Tarea(nombreTarea, EstadoTarea.ABIERTA);
        repository.guardar(tarea);
    }


    @Cuando("intento guardar la carga")
    public void intento_guardar_la_carga() {
        try {
            excepcion = null;
            servicio.cargarHoras(nombreTarea, fechaSeleccionada, horasIngresadas);
        } catch (Exception e) {
            excepcion = e;
        }
    }

    @Cuando("intento registrar horas")
    public void intento_registrar_horas() {
        try {
            excepcion = null;
            servicio.cargarHoras(nombreTarea, fechaSeleccionada, horasIngresadas);
        } catch (Exception e) {
            excepcion = e;
        }
    }


    @Entonces("el sistema muestra el mensaje {string}")
    public void el_sistema_muestra_el_mensaje(String mensajeEsperado) {
        assertNotNull(excepcion, "Se esperaba una excepción, pero no se lanzó ninguna");
        assertEquals(mensajeEsperado, excepcion.getMessage());
    }
}
