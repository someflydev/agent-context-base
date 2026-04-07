package dev.agentcontext.taskflow.core;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.List;

public final class JobLoader {
    private static final ObjectMapper MAPPER = new ObjectMapper().findAndRegisterModules();

    private JobLoader() {
    }

    public static Path defaultFixturesPath() {
        String env = System.getenv("TASKFLOW_FIXTURES_PATH");
        if (env != null && !env.isBlank()) {
            return Path.of(env).toAbsolutePath().normalize();
        }
        return Path.of("..", "fixtures").toAbsolutePath().normalize();
    }

    private static <T> T loadJson(Path fixturesPath, String filename, TypeReference<T> typeReference) {
        Path target = fixturesPath.toAbsolutePath().normalize().resolve(filename);
        if (!Files.exists(fixturesPath)) {
            throw new FixtureException("fixtures path does not exist: " + fixturesPath);
        }
        if (!Files.exists(target)) {
            throw new FixtureException("missing fixture file: " + target);
        }
        try {
            return MAPPER.readValue(target.toFile(), typeReference);
        } catch (IOException error) {
            throw new FixtureException("failed to load " + target + ": " + error.getMessage(), error);
        }
    }

    public static List<Job> loadJobs(Path fixturesPath) {
        return loadJson(fixturesPath, "jobs.json", new TypeReference<List<Job>>() {
        });
    }

    public static List<Event> loadEvents(Path fixturesPath) {
        List<Event> events = loadJson(fixturesPath, "events.json", new TypeReference<List<Event>>() {
        });
        events.sort(Comparator.comparing(Event::timestamp));
        return events;
    }

    public static Config loadConfig(Path fixturesPath) {
        return loadJson(fixturesPath, "config.json", new TypeReference<Config>() {
        });
    }
}
