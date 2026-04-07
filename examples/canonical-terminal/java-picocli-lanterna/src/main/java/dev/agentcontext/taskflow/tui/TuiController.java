package dev.agentcontext.taskflow.tui;

import com.googlecode.lanterna.input.KeyStroke;
import com.googlecode.lanterna.input.KeyType;
import dev.agentcontext.taskflow.core.Config;
import dev.agentcontext.taskflow.core.Job;
import dev.agentcontext.taskflow.core.JobLoader;
import dev.agentcontext.taskflow.core.Stats;
import dev.agentcontext.taskflow.core.StatsComputer;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;

public final class TuiController {
    private final Path fixturesPath;
    private final int interval;
    private int selectedIndex = 0;

    public TuiController(Path fixturesPath, int interval) {
        this.fixturesPath = fixturesPath;
        this.interval = interval;
    }

    public void run() {
        try {
            TaskflowApp.Runtime runtime = new TaskflowApp().create();
            refresh(runtime);
            runtime.gui().addWindow(runtime.window());
            while (true) {
                KeyStroke key = runtime.screen().readInput();
                if (key == null) {
                    continue;
                }
                if (key.getKeyType() == KeyType.EOF || key.getKeyType() == KeyType.Escape ||
                    (key.getCharacter() != null && key.getCharacter() == 'q')) {
                    break;
                }
                if (key.getKeyType() == KeyType.ArrowDown) {
                    selectedIndex += 1;
                } else if (key.getKeyType() == KeyType.ArrowUp) {
                    selectedIndex = Math.max(selectedIndex - 1, 0);
                } else if (key.getCharacter() != null && key.getCharacter() == 'r') {
                    refresh(runtime);
                    continue;
                }
                refresh(runtime);
            }
            runtime.screen().stopScreen();
        } catch (IOException error) {
            throw new IllegalStateException("failed to run Lanterna UI", error);
        }
    }

    private void refresh(TaskflowApp.Runtime runtime) {
        List<Job> jobs = JobLoader.loadJobs(fixturesPath);
        Config config = JobLoader.loadConfig(fixturesPath);
        Stats stats = StatsComputer.computeStats(jobs);
        selectedIndex = Math.min(selectedIndex, Math.max(jobs.size() - 1, 0));
        runtime.header().setText(
            "Queue " + config.queueName() + " | total " + stats.total() + " | done " + stats.byStatus().get("done") +
                " | failed " + stats.byStatus().get("failed") + " | running " + stats.byStatus().get("running") +
                " | pending " + stats.byStatus().get("pending")
        );
        runtime.footer().setText("Keys: q quit | arrows navigate | r refresh | interval " + interval + "s");
        runtime.jobList().setJobs(jobs, () -> runtime.detail().setJob(jobs.get(runtime.jobList().view().getSelectedIndex())), () -> selectedIndex);
        runtime.detail().setJob(jobs.isEmpty() ? null : jobs.get(selectedIndex));
    }
}
