package dev.agentcontext.taskflow.tui;

import com.googlecode.lanterna.gui2.TextBox;
import dev.agentcontext.taskflow.core.Job;
import java.util.List;

public final class JobDetailComponent {
    private final TextBox textBox = new TextBox();

    public TextBox view() {
        textBox.setReadOnly(true);
        return textBox;
    }

    public void setJob(Job job) {
        if (job == null) {
            textBox.setText("No job selected.");
            return;
        }
        List<String> lines = new java.util.ArrayList<>();
        lines.add(job.name());
        lines.add("ID: " + job.id());
        lines.add("Status: " + job.status().value());
        lines.add("Started: " + (job.startedAt() == null ? "-" : job.startedAt()));
        lines.add("Duration: " + (job.durationS() == null ? "-" : job.durationS()) + "s");
        lines.add("Tags: " + String.join(", ", job.tags()));
        lines.add("");
        lines.add("Output:");
        for (String line : job.outputLines()) {
            lines.add("- " + line);
        }
        textBox.setText(String.join(System.lineSeparator(), lines));
    }
}
