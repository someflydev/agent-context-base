package cmd

import (
	"github.com/agent-context-base/taskflow-go-bubbletea/internal/cli"
	"github.com/agent-context-base/taskflow-go-bubbletea/internal/core"
	"github.com/agent-context-base/taskflow-go-bubbletea/internal/tui"
	"github.com/spf13/cobra"
)

func init() {
	var interval int
	var noTUI bool

	command := &cobra.Command{
		Use:   "watch",
		Short: "Watch jobs",
		RunE: func(cmd *cobra.Command, args []string) error {
			jobs, err := core.LoadJobs(fixtureRoot())
			if err != nil {
				return cli.PrintError(err)
			}
			if noTUI {
				cli.PrintMarkerBlock("## BEGIN_JOBS ##", cli.JobsTable(core.SortJobs(jobs)), "## END_JOBS ##")
				return nil
			}
			events, err := core.LoadEvents(fixtureRoot())
			if err != nil {
				return cli.PrintError(err)
			}
			if _, err := core.LoadConfig(fixtureRoot()); err != nil {
				return cli.PrintError(err)
			}
			return tui.Run(jobs, events, interval)
		},
	}
	command.Flags().IntVar(&interval, "interval", 5, "Refresh interval in seconds")
	command.Flags().BoolVar(&noTUI, "no-tui", false, "Print a non-interactive snapshot")
	rootCmd.AddCommand(command)
}
