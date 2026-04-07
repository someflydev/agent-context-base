package dev.agentcontext.taskflow.cli;

import dev.agentcontext.taskflow.core.FixtureException;
import dev.agentcontext.taskflow.core.Job;
import dev.agentcontext.taskflow.core.JobFilter;
import dev.agentcontext.taskflow.core.JobLoader;
import java.util.List;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;
import picocli.CommandLine.ParentCommand;

@Command(name = "list")
public class ListCommand implements Runnable {
    @ParentCommand
    TaskflowCommand parent;

    @Option(names = "--status")
    String status;

    @Option(names = "--tag")
    String tag;

    @Option(names = "--output", defaultValue = "table")
    String output;

    @Override
    public void run() {
        try {
            List<Job> jobs = JobFilter.filterJobs(JobLoader.loadJobs(parent.fixturesPath()), status, tag);
            if ("json".equals(output)) {
                System.out.println(OutputFormatter.json(jobs));
                return;
            }
            System.out.println(OutputFormatter.markerWrap("## BEGIN_JOBS ##", OutputFormatter.jobsTable(jobs), "## END_JOBS ##"));
        } catch (FixtureException error) {
            System.err.println(OutputFormatter.markerWrap("## BEGIN_ERROR ##", error.getMessage(), "## END_ERROR ##"));
            throw error;
        }
    }
}
