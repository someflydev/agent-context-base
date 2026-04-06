package cmd

import (
	"github.com/agent-context-base/taskflow-go-bubbletea/internal/cli"
	"github.com/agent-context-base/taskflow-go-bubbletea/internal/core"
	"github.com/spf13/cobra"
)

func init() {
	var output string

	command := &cobra.Command{
		Use:   "stats",
		Short: "Print job stats",
		RunE: func(cmd *cobra.Command, args []string) error {
			jobs, err := core.LoadJobs(fixtureRoot())
			if err != nil {
				return cli.PrintError(err)
			}
			stats := core.ComputeStats(jobs)
			if output == "json" {
				return cli.PrintJSON(stats)
			}
			cli.PrintMarkerBlock("## BEGIN_STATS ##", cli.StatsPlain(stats), "## END_STATS ##")
			return nil
		},
	}
	command.Flags().StringVar(&output, "output", "plain", "Output format: json or plain")
	rootCmd.AddCommand(command)
}
