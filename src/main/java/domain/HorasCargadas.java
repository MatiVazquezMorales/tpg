package domain;

import java.time.LocalDate;

public class HorasCargadas {
    private final LocalDate fecha;
    private final int horas;

    public HorasCargadas(LocalDate fecha, int horas) {
        this.fecha = fecha;
        this.horas = horas;
    }

    public LocalDate getFecha() {
        return fecha;
    }

    public int getHoras() {
        return horas;
    }
}
