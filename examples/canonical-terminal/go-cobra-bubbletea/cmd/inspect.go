package cmd

import (
	"fmt"

	"github.com/agent-context-base/taskflow-go-bubbletea/internal/cli"
	"github.com/agent-context-base/taskflow-go-bubbletea/internal/core"
	"github.com/spf13/cobra"
)

func init() {
	var output string

	command := &cobra.Command{
		Use:   "inspect JOB_ID",
		Short: "Inspect a job",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			jobs, err := core.LoadJobs(fixtureRoot())
			if err != nil {
				return cli.PrintError(err)
			}
			job := core.FindJob(jobs, args[0])
			if job == nil {
				return cli.PrintError(fmt.Errorf("job not found: %s", args[0]))
			}
			if output == "json" {
				return cli.PrintJSON(job)
			}
			cli.PrintMarkerBlock("## BEGIN_JOB_DETAIL ##", cli.JobPlain(*job), "## END_JOB_DETAIL ##")
			return nil
		},
	}
	command.Flags().StringVar(&output, "output", "plain", "Output format: json or plain")
	rootCmd.AddCommand(command)
}
