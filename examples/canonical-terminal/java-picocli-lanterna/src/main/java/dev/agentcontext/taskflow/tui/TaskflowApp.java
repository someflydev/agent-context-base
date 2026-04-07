package dev.agentcontext.taskflow.tui;

import com.googlecode.lanterna.TerminalSize;
import com.googlecode.lanterna.gui2.BasicWindow;
import com.googlecode.lanterna.gui2.Borders;
import com.googlecode.lanterna.gui2.Direction;
import com.googlecode.lanterna.gui2.Label;
import com.googlecode.lanterna.gui2.LinearLayout;
import com.googlecode.lanterna.gui2.MultiWindowTextGUI;
import com.googlecode.lanterna.gui2.Panel;
import com.googlecode.lanterna.gui2.SeparateTextGUIThread;
import com.googlecode.lanterna.gui2.WindowBasedTextGUI;
import com.googlecode.lanterna.screen.Screen;
import com.googlecode.lanterna.screen.TerminalScreen;
import com.googlecode.lanterna.terminal.DefaultTerminalFactory;
import java.io.IOException;

public final class TaskflowApp {
    public record Runtime(Screen screen, WindowBasedTextGUI gui, BasicWindow window, Label header, Label footer,
                          JobListComponent jobList, JobDetailComponent detail) {
    }

    public Runtime create() throws IOException {
        TerminalScreen screen = new TerminalScreen(new DefaultTerminalFactory().setInitialTerminalSize(new TerminalSize(120, 32)).createTerminal());
        screen.startScreen();
        BasicWindow window = new BasicWindow("TaskFlow Monitor");
        Panel root = new Panel(new LinearLayout(Direction.VERTICAL));
        Label header = new Label("Loading...");
        Label footer = new Label("Keys: q quit | arrows navigate | r refresh");
        JobListComponent jobList = new JobListComponent();
        JobDetailComponent detail = new JobDetailComponent();

        Panel body = new Panel(new LinearLayout(Direction.HORIZONTAL));
        body.addComponent(jobList.view().withBorder(Borders.singleLine("Jobs")));
        body.addComponent(detail.view().withBorder(Borders.singleLine("Detail")));

        root.addComponent(header);
        root.addComponent(body);
        root.addComponent(footer);
        window.setComponent(root);

        MultiWindowTextGUI gui = new MultiWindowTextGUI(new SeparateTextGUIThread.Factory(), screen);
        return new Runtime(screen, gui, window, header, footer, jobList, detail);
    }
}
