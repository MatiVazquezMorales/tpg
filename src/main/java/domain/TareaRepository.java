package domain;

import java.util.List;
import java.util.Optional;

public interface TareaRepository {
    void guardar(Tarea tarea);

    Optional<Tarea> buscarPorNombre(String nombre);

    List<Tarea> buscarTodos();

    List<Tarea> buscarPorEstado(EstadoTarea estado);

    boolean existe(String nombre);

}