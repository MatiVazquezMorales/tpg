package steps;

import domain.TareaRepository;
import domain.InMemoryTareaRepository;
import java.time.LocalDate;

public class TestContext {
    private static TareaRepository repository;

    public static TareaRepository getRepository() {
        if (repository == null) {
            repository = new InMemoryTareaRepository();
        }
        return repository;
    }

    public static void reset() {
        repository = new InMemoryTareaRepository();
    }
}
