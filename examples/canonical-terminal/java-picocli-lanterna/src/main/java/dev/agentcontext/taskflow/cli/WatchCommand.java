package dev.agentcontext.taskflow.cli;

import dev.agentcontext.taskflow.core.FixtureException;
import dev.agentcontext.taskflow.core.Job;
import dev.agentcontext.taskflow.core.JobFilter;
import dev.agentcontext.taskflow.core.JobLoader;
import dev.agentcontext.taskflow.tui.TuiController;
import java.util.List;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;
import picocli.CommandLine.ParentCommand;

@Command(name = "watch")
public class WatchCommand implements Runnable {
    @ParentCommand
    TaskflowCommand parent;

    @Option(names = "--no-tui")
    boolean noTui;

    @Option(names = "--interval", defaultValue = "5")
    int interval;

    @Override
    public void run() {
        try {
            List<Job> jobs = JobFilter.filterJobs(JobLoader.loadJobs(parent.fixturesPath()), null, null);
            if (noTui || System.console() == null) {
                System.out.println(OutputFormatter.markerWrap("## BEGIN_JOBS ##", OutputFormatter.jobsTable(jobs), "## END_JOBS ##"));
                return;
            }
            new TuiController(parent.fixturesPath(), interval).run();
        } catch (FixtureException error) {
            System.err.println(OutputFormatter.markerWrap("## BEGIN_ERROR ##", error.getMessage(), "## END_ERROR ##"));
            throw error;
        }
    }
}
