package dev.agentcontext.taskflow.repl;

import dev.agentcontext.taskflow.cli.TaskflowMain;
import dev.agentcontext.taskflow.core.Job;
import dev.agentcontext.taskflow.core.JobLoader;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import org.jline.reader.EndOfFileException;
import org.jline.reader.LineReader;
import org.jline.reader.LineReaderBuilder;
import org.jline.reader.UserInterruptException;
import org.jline.reader.impl.history.DefaultHistory;
import org.jline.terminal.Terminal;
import org.jline.terminal.TerminalBuilder;

public final class ReplShell {
    private final Path fixturesPath;

    public ReplShell(Path fixturesPath) {
        this.fixturesPath = fixturesPath;
    }

    public void run() {
        try {
            List<Job> jobs = JobLoader.loadJobs(fixturesPath);
            Terminal terminal = TerminalBuilder.builder().system(true).build();
            LineReader reader = LineReaderBuilder.builder()
                .terminal(terminal)
                .history(new DefaultHistory())
                .completer(new TaskflowCompleter(jobs))
                .build();

            while (true) {
                String line;
                try {
                    line = reader.readLine("taskflow> ").trim();
                } catch (UserInterruptException interrupt) {
                    continue;
                } catch (EndOfFileException eof) {
                    break;
                }
                if (line.isBlank()) {
                    continue;
                }
                if ("quit".equals(line) || "exit".equals(line)) {
                    break;
                }
                TaskflowMain.execute(fixturesPath, line.split("\\s+"));
            }
        } catch (IOException error) {
            throw new IllegalStateException("failed to start JLine shell", error);
        }
    }
}
