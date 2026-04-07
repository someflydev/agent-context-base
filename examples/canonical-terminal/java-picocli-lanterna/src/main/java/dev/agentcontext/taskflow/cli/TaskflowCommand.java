package dev.agentcontext.taskflow.cli;

import java.nio.file.Path;
import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;

@Command(
    name = "taskflow",
    mixinStandardHelpOptions = true,
    subcommands = {ListCommand.class, InspectCommand.class, StatsCommand.class, WatchCommand.class}
)
public class TaskflowCommand implements Runnable {
    @Option(names = "--fixtures-path", description = "Override fixture corpus path")
    Path fixturesPath;

    Path fixturesPath() {
        return fixturesPath == null
            ? dev.agentcontext.taskflow.core.JobLoader.defaultFixturesPath()
            : fixturesPath.toAbsolutePath().normalize();
    }

    @Override
    public void run() {
        CommandLine.usage(this, System.out);
    }

    public static void main(String[] args) {
        int exitCode = new CommandLine(new TaskflowCommand()).execute(args);
        System.exit(exitCode);
    }
}
