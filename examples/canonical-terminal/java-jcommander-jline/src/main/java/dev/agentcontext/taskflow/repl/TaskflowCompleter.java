package dev.agentcontext.taskflow.repl;

import dev.agentcontext.taskflow.core.Job;
import java.util.ArrayList;
import java.util.List;
import org.jline.reader.Candidate;
import org.jline.reader.Completer;
import org.jline.reader.LineReader;
import org.jline.reader.ParsedLine;

public final class TaskflowCompleter implements Completer {
    private final List<String> jobIds;

    public TaskflowCompleter(List<Job> jobs) {
        this.jobIds = jobs.stream().map(Job::id).toList();
    }

    @Override
    public void complete(LineReader reader, ParsedLine line, List<Candidate> candidates) {
        List<String> words = new ArrayList<>(line.words());
        if (words.isEmpty()) {
            for (String command : List.of("list", "inspect", "stats", "filter", "quit")) {
                candidates.add(new Candidate(command));
            }
            return;
        }
        if ("inspect".equals(words.get(0)) && words.size() <= 2) {
            for (String jobId : jobIds) {
                candidates.add(new Candidate(jobId));
            }
        }
        if ("filter".equals(words.get(0))) {
            for (String status : List.of("status:pending", "status:running", "status:done", "status:failed")) {
                candidates.add(new Candidate(status));
            }
        }
    }
}
