package dev.agentcontext.taskflow.core;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum JobStatus {
    PENDING("pending"),
    RUNNING("running"),
    DONE("done"),
    FAILED("failed");

    private final String value;

    JobStatus(String value) {
        this.value = value;
    }

    @JsonValue
    public String value() {
        return value;
    }

    @JsonCreator
    public static JobStatus fromValue(String value) {
        for (JobStatus status : values()) {
            if (status.value.equalsIgnoreCase(value)) {
                return status;
            }
        }
        throw new IllegalArgumentException("unknown status: " + value);
    }
}
