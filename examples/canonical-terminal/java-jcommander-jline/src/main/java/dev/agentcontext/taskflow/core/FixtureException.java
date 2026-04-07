package dev.agentcontext.taskflow.core;

public class FixtureException extends RuntimeException {
    public FixtureException(String message, Throwable cause) {
        super(message, cause);
    }

    public FixtureException(String message) {
        super(message);
    }
}
