package dev.agentcontext.taskflow.cli;

import dev.agentcontext.taskflow.core.FixtureException;
import dev.agentcontext.taskflow.core.Job;
import dev.agentcontext.taskflow.core.JobLoader;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;
import picocli.CommandLine.Parameters;
import picocli.CommandLine.ParentCommand;

@Command(name = "inspect")
public class InspectCommand implements Runnable {
    @ParentCommand
    TaskflowCommand parent;

    @Parameters(index = "0")
    String jobId;

    @Option(names = "--output", defaultValue = "plain")
    String output;

    @Override
    public void run() {
        try {
            Job job = JobLoader.loadJobs(parent.fixturesPath()).stream()
                .filter(item -> item.id().equals(jobId))
                .findFirst()
                .orElseThrow(() -> new FixtureException("job not found: " + jobId));
            if ("json".equals(output)) {
                System.out.println(OutputFormatter.json(job));
                return;
            }
            System.out.println(OutputFormatter.markerWrap("## BEGIN_JOB_DETAIL ##", OutputFormatter.jobPlain(job), "## END_JOB_DETAIL ##"));
        } catch (FixtureException error) {
            System.err.println(OutputFormatter.markerWrap("## BEGIN_ERROR ##", error.getMessage(), "## END_ERROR ##"));
            throw error;
        }
    }
}
