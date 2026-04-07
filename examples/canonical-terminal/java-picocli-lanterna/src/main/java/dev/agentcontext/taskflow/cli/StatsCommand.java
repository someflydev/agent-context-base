package dev.agentcontext.taskflow.cli;

import dev.agentcontext.taskflow.core.FixtureException;
import dev.agentcontext.taskflow.core.JobLoader;
import dev.agentcontext.taskflow.core.Stats;
import dev.agentcontext.taskflow.core.StatsComputer;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;
import picocli.CommandLine.ParentCommand;

@Command(name = "stats")
public class StatsCommand implements Runnable {
    @ParentCommand
    TaskflowCommand parent;

    @Option(names = "--output", defaultValue = "plain")
    String output;

    @Override
    public void run() {
        try {
            Stats stats = StatsComputer.computeStats(JobLoader.loadJobs(parent.fixturesPath()));
            if ("json".equals(output)) {
                System.out.println(OutputFormatter.json(stats));
                return;
            }
            System.out.println(OutputFormatter.markerWrap("## BEGIN_STATS ##", OutputFormatter.statsPlain(stats), "## END_STATS ##"));
        } catch (FixtureException error) {
            System.err.println(OutputFormatter.markerWrap("## BEGIN_ERROR ##", error.getMessage(), "## END_ERROR ##"));
            throw error;
        }
    }
}
