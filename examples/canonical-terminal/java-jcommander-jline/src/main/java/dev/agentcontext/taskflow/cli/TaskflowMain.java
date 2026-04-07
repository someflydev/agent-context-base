package dev.agentcontext.taskflow.cli;

import com.beust.jcommander.JCommander;
import dev.agentcontext.taskflow.core.FixtureException;
import dev.agentcontext.taskflow.core.Job;
import dev.agentcontext.taskflow.core.JobFilter;
import dev.agentcontext.taskflow.core.JobLoader;
import dev.agentcontext.taskflow.core.StatsComputer;
import dev.agentcontext.taskflow.repl.ReplShell;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;

public final class TaskflowMain {
    private TaskflowMain() {
    }

    public static void main(String[] args) {
        TaskflowOptions options = new TaskflowOptions();
        JCommander commander = JCommander.newBuilder().addObject(options).build();
        commander.parse(args);
        Path fixturesPath = options.fixturesPath == null ? JobLoader.defaultFixturesPath() : Path.of(options.fixturesPath).toAbsolutePath().normalize();
        if (options.command.isEmpty()) {
            commander.usage();
            return;
        }
        execute(fixturesPath, options.command.toArray(String[]::new));
    }

    public static void execute(Path fixturesPath, String... args) {
        try {
            String command = args[0];
            switch (command) {
                case "list" -> runList(fixturesPath, Arrays.copyOfRange(args, 1, args.length));
                case "inspect" -> runInspect(fixturesPath, Arrays.copyOfRange(args, 1, args.length));
                case "stats" -> runStats(fixturesPath, Arrays.copyOfRange(args, 1, args.length));
                case "watch" -> runWatch(fixturesPath, Arrays.copyOfRange(args, 1, args.length));
                default -> throw new FixtureException("unknown command: " + command);
            }
        } catch (FixtureException error) {
            System.err.println(OutputFormatter.markerWrap("## BEGIN_ERROR ##", error.getMessage(), "## END_ERROR ##"));
            throw error;
        }
    }

    private static void runList(Path fixturesPath, String[] args) {
        String status = optionValue(args, "--status");
        String tag = optionValue(args, "--tag");
        String output = optionValue(args, "--output", "table");
        List<Job> jobs = JobFilter.filterJobs(JobLoader.loadJobs(fixturesPath), status, tag);
        if ("json".equals(output)) {
            System.out.println(OutputFormatter.json(jobs));
            return;
        }
        System.out.println(OutputFormatter.markerWrap("## BEGIN_JOBS ##", OutputFormatter.jobsTable(jobs), "## END_JOBS ##"));
    }

    private static void runInspect(Path fixturesPath, String[] args) {
        if (args.length == 0) {
            throw new FixtureException("inspect requires a job id");
        }
        String jobId = args[0];
        String output = optionValue(Arrays.copyOfRange(args, 1, args.length), "--output", "plain");
        Job job = JobLoader.loadJobs(fixturesPath).stream()
            .filter(item -> item.id().equals(jobId))
            .findFirst()
            .orElseThrow(() -> new FixtureException("job not found: " + jobId));
        if ("json".equals(output)) {
            System.out.println(OutputFormatter.json(job));
            return;
        }
        System.out.println(OutputFormatter.markerWrap("## BEGIN_JOB_DETAIL ##", OutputFormatter.jobPlain(job), "## END_JOB_DETAIL ##"));
    }

    private static void runStats(Path fixturesPath, String[] args) {
        String output = optionValue(args, "--output", "plain");
        var stats = StatsComputer.computeStats(JobLoader.loadJobs(fixturesPath));
        if ("json".equals(output)) {
            System.out.println(OutputFormatter.json(stats));
            return;
        }
        System.out.println(OutputFormatter.markerWrap("## BEGIN_STATS ##", OutputFormatter.statsPlain(stats), "## END_STATS ##"));
    }

    private static void runWatch(Path fixturesPath, String[] args) {
        boolean noRepl = Arrays.asList(args).contains("--no-repl");
        if (noRepl || System.console() == null) {
            List<Job> jobs = JobFilter.filterJobs(JobLoader.loadJobs(fixturesPath), null, null);
            System.out.println(OutputFormatter.markerWrap("## BEGIN_JOBS ##", OutputFormatter.jobsTable(jobs), "## END_JOBS ##"));
            return;
        }
        new ReplShell(fixturesPath).run();
    }

    private static String optionValue(String[] args, String flag) {
        return optionValue(args, flag, null);
    }

    private static String optionValue(String[] args, String flag, String fallback) {
        for (int index = 0; index < args.length - 1; index += 1) {
            if (flag.equals(args[index])) {
                return args[index + 1];
            }
        }
        return fallback;
    }
}
