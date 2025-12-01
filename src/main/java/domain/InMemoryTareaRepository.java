package domain;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

public class InMemoryTareaRepository implements TareaRepository {
    private final List<Tarea> tareas = new ArrayList<>();

    @Override
    public void guardar(Tarea tarea) {
        tareas.add(tarea);
    }

    @Override
    public Optional<Tarea> buscarPorNombre(String nombre) {
        return tareas.stream().filter(c -> c.getNombre().equals(nombre)).findFirst();
    }

    @Override
    public List<Tarea> buscarTodos() {
        return new ArrayList<>(tareas);
    }

    @Override
    public List<Tarea> buscarPorEstado(EstadoTarea estado) {
        return tareas.stream()
                .filter(c -> c.getEstado() == estado)
                .collect(Collectors.toList());
    }

    @Override
    public boolean existe(String nombre) {
        return buscarPorNombre(nombre).isPresent();
    }
}