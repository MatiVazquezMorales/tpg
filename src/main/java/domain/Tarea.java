package domain;

import java.util.ArrayList;
import java.util.List;
import domain.HorasCargadas;

public class Tarea {
    private String nombre;
    private EstadoTarea estado;
    private List<HorasCargadas> horas = new ArrayList<>();

    public Tarea(String nombre, EstadoTarea estado) {
        this.nombre = nombre;
        this.estado = estado;
    }

    public String getNombre() {
        return nombre;
    }

    public EstadoTarea getEstado() {
        return estado;
    }

    public void agregarHoras(HorasCargadas carga) {
        horas.add(carga);
    }

    public List<HorasCargadas> getHoras() {
        return horas;
    }
}
