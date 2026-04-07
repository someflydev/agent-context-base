package dev.agentcontext.taskflow;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.agentcontext.taskflow.cli.TaskflowMain;
import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

class SmokeCliTest {
    private static final Path FIXTURES = Path.of("..", "fixtures").toAbsolutePath().normalize();

    private String captureOut(String... args) {
        PrintStream originalOut = System.out;
        ByteArrayOutputStream output = new ByteArrayOutputStream();
        try {
            System.setOut(new PrintStream(output, true, StandardCharsets.UTF_8));
            TaskflowMain.execute(FIXTURES, args);
            return output.toString(StandardCharsets.UTF_8);
        } finally {
            System.setOut(originalOut);
        }
    }

    @Test
    void listTable() {
        assertTrue(captureOut("list").contains("## BEGIN_JOBS ##"));
    }

    @Test
    void listJson() {
        assertTrue(captureOut("list", "--output", "json").contains("\"id\""));
    }

    @Test
    void filterStatus() {
        assertTrue(captureOut("list", "--status", "done", "--output", "json").contains("\"status\""));
    }

    @Test
    void inspectJob() {
        assertTrue(captureOut("inspect", "job-001", "--output", "json").contains("job-001"));
    }

    @Test
    void statsJson() {
        assertTrue(captureOut("stats", "--output", "json").contains("\"total\" : 20") || captureOut("stats", "--output", "json").contains("\"total\":20"));
    }

    @Test
    void watchNoRepl() {
        assertTrue(captureOut("watch", "--no-repl").contains("## BEGIN_JOBS ##"));
    }

    @Test
    void missingFixturesFails() {
        try {
            TaskflowMain.execute(FIXTURES.resolve("missing"), "list");
        } catch (RuntimeException error) {
            assertTrue(error.getMessage().contains("fixtures path does not exist"));
            return;
        }
        throw new AssertionError("expected runtime exception");
    }

    @Test
    void processLevelInvocationWorks() throws Exception {
        String javaBin = Path.of(System.getProperty("java.home"), "bin", "java").toString();
        Process process = new ProcessBuilder(
            javaBin,
            "-cp",
            System.getProperty("java.class.path"),
            "dev.agentcontext.taskflow.cli.TaskflowMain",
            "--fixtures-path",
            FIXTURES.toString(),
            "stats",
            "--output",
            "json"
        ).redirectErrorStream(true).start();
        String output;
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            output = reader.lines().reduce("", (left, right) -> left + right + "\n");
        }
        assertEquals(0, process.waitFor());
        assertTrue(output.contains("\"total\""));
    }
}
