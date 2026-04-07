package dev.agentcontext.taskflow;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.agentcontext.taskflow.core.JobFilter;
import dev.agentcontext.taskflow.core.JobLoader;
import dev.agentcontext.taskflow.core.StatsComputer;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

class CoreTest {
    private static final Path FIXTURES = Path.of("..", "fixtures").toAbsolutePath().normalize();

    @Test
    void loadsSharedFixtures() {
        assertEquals(20, JobLoader.loadJobs(FIXTURES).size());
        assertTrue(JobLoader.loadEvents(FIXTURES).size() >= 40);
        assertTrue(JobLoader.loadConfig(FIXTURES).fixtureMode());
    }

    @Test
    void filtersAndComputesStats() {
        var jobs = JobLoader.loadJobs(FIXTURES);
        assertTrue(JobFilter.filterJobs(jobs, "failed", null).stream().allMatch(job -> job.status().value().equals("failed")));
        assertEquals(20, StatsComputer.computeStats(jobs).total());
    }
}
