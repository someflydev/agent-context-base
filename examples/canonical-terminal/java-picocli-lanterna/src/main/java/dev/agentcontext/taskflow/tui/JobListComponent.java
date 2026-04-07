package dev.agentcontext.taskflow.tui;

import com.googlecode.lanterna.gui2.ActionListBox;
import dev.agentcontext.taskflow.core.Job;
import java.util.List;

public final class JobListComponent {
    private final ActionListBox listBox = new ActionListBox();

    public ActionListBox view() {
        return listBox;
    }

    public void setJobs(List<Job> jobs, Runnable onSelect, java.util.function.IntSupplier indexSupplier) {
        listBox.clearItems();
        for (int index = 0; index < jobs.size(); index += 1) {
            Job job = jobs.get(index);
            int selectedIndex = index;
            listBox.addItem(job.id() + " " + job.name() + " [" + job.status().value() + "]", () -> {
                listBox.setSelectedIndex(selectedIndex);
                onSelect.run();
            });
        }
        if (!jobs.isEmpty()) {
            listBox.setSelectedIndex(Math.min(indexSupplier.getAsInt(), jobs.size() - 1));
        }
    }
}
