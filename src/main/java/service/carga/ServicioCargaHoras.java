package service.carga;

import domain.EstadoTarea;
import domain.HorasCargadas;
import domain.Tarea;
import domain.TareaRepository;

import java.time.LocalDate;

public class ServicioCargaHoras {

    private final TareaRepository repository;

    public ServicioCargaHoras(TareaRepository repository) {
        this.repository = repository;
    }

    public void cargarHoras(String nombreTarea, LocalDate fecha, int horas) {

        Tarea tarea = repository.buscarPorNombre(nombreTarea)
                .orElseThrow(() -> new IllegalArgumentException("La tarea no existe"));

        if (tarea.getEstado() == EstadoTarea.CERRADA) {
            throw new IllegalArgumentException("No se pueden cargar horas en tareas cerradas");
        }

        if (tarea.getEstado() == EstadoTarea.NOINICIADA) {
            throw new IllegalArgumentException("No puede registrar horas en tareas no iniciadas");
        }

        if (horas > 24) {
            throw new IllegalArgumentException("No se pueden registrar más de 24 horas por día");
        }

        if (fecha.isAfter(LocalDate.now())) {
            throw new IllegalArgumentException("No se pueden cargar horas de fechas futuras");
        }

        tarea.agregarHoras(new HorasCargadas(fecha, horas));
    }
}
