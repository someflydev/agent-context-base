package dev.agentcontext.taskflow.cli;

import com.beust.jcommander.Parameter;
import java.util.ArrayList;
import java.util.List;

public class TaskflowOptions {
    @Parameter(names = "--fixtures-path")
    public String fixturesPath;

    @Parameter(description = "command arguments")
    public List<String> command = new ArrayList<>();
}
