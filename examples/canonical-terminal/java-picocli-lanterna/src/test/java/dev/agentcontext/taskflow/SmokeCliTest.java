package dev.agentcontext.taskflow;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.agentcontext.taskflow.cli.TaskflowCommand;
import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import picocli.CommandLine;

class SmokeCliTest {
    private static final String FIXTURES = Path.of("..", "fixtures").toAbsolutePath().normalize().toString();

    private String run(String... args) {
        PrintStream originalOut = System.out;
        PrintStream originalErr = System.err;
        ByteArrayOutputStream output = new ByteArrayOutputStream();
        try {
            System.setOut(new PrintStream(output, true, StandardCharsets.UTF_8));
            System.setErr(new PrintStream(output, true, StandardCharsets.UTF_8));
            CommandLine commandLine = new CommandLine(new TaskflowCommand());
            int exitCode = commandLine.execute(args);
            assertEquals(0, exitCode, output.toString(StandardCharsets.UTF_8));
            return output.toString(StandardCharsets.UTF_8);
        } finally {
            System.setOut(originalOut);
            System.setErr(originalErr);
        }
    }

    @Test
    void listTable() {
        String output = run("--fixtures-path", FIXTURES, "list");
        assertTrue(output.contains("## BEGIN_JOBS ##"));
    }

    @Test
    void listJson() {
        String output = run("--fixtures-path", FIXTURES, "list", "--output", "json");
        assertTrue(output.contains("\"id\""));
    }

    @Test
    void filterStatus() {
        String output = run("--fixtures-path", FIXTURES, "list", "--status", "done", "--output", "json");
        assertTrue(output.contains("\"status\" : \"done\"") || output.contains("\"status\":\"done\""));
    }

    @Test
    void inspectJob() {
        String output = run("--fixtures-path", FIXTURES, "inspect", "job-001", "--output", "json");
        assertTrue(output.contains("\"id\""));
        assertTrue(output.contains("job-001"));
    }

    @Test
    void statsJson() {
        String output = run("--fixtures-path", FIXTURES, "stats", "--output", "json");
        assertTrue(output.contains("\"total\" : 20") || output.contains("\"total\":20"));
    }

    @Test
    void watchNoTui() {
        String output = run("--fixtures-path", FIXTURES, "watch", "--no-tui");
        assertTrue(output.contains("## BEGIN_JOBS ##"));
    }

    @Test
    void missingFixturesFails() {
        PrintStream originalOut = System.out;
        PrintStream originalErr = System.err;
        ByteArrayOutputStream output = new ByteArrayOutputStream();
        try {
            System.setOut(new PrintStream(output, true, StandardCharsets.UTF_8));
            System.setErr(new PrintStream(output, true, StandardCharsets.UTF_8));
            CommandLine commandLine = new CommandLine(new TaskflowCommand());
            int exitCode = commandLine.execute("--fixtures-path", Path.of(FIXTURES, "missing").toString(), "list");
            assertNotEquals(0, exitCode);
        } finally {
            System.setOut(originalOut);
            System.setErr(originalErr);
        }
    }

    @Test
    void processLevelInvocationWorks() throws Exception {
        String javaBin = Path.of(System.getProperty("java.home"), "bin", "java").toString();
        Process process = new ProcessBuilder(
            javaBin,
            "-cp",
            System.getProperty("java.class.path"),
            "dev.agentcontext.taskflow.cli.TaskflowCommand",
            "--fixtures-path",
            FIXTURES,
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
