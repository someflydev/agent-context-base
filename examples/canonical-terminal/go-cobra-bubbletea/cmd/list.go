package cmd

import (
	"github.com/agent-context-base/taskflow-go-bubbletea/internal/cli"
	"github.com/agent-context-base/taskflow-go-bubbletea/internal/core"
	"github.com/spf13/cobra"
)

func init() {
	var status string
	var tag string
	var output string

	command := &cobra.Command{
		Use:   "list",
		Short: "List jobs",
		RunE: func(cmd *cobra.Command, args []string) error {
			jobs, err := core.LoadJobs(fixtureRoot())
			if err != nil {
				return cli.PrintError(err)
			}
			filtered := core.SortJobs(core.FilterJobs(jobs, status, tag))
			if output == "json" {
				return cli.PrintJSON(filtered)
			}
			cli.PrintMarkerBlock("## BEGIN_JOBS ##", cli.JobsTable(filtered), "## END_JOBS ##")
			return nil
		},
	}
	command.Flags().StringVar(&status, "status", "", "Optional status filter")
	command.Flags().StringVar(&tag, "tag", "", "Optional tag filter")
	command.Flags().StringVar(&output, "output", "table", "Output format: json or table")
	rootCmd.AddCommand(command)
}
