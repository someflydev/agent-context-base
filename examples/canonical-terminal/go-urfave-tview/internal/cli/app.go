package cli

import (
	"fmt"

	"github.com/agent-context-base/taskflow-go-tview/internal/core"
	"github.com/agent-context-base/taskflow-go-tview/internal/tui"
	ucli "github.com/urfave/cli/v2"
)

func NewApp() *ucli.App {
	return &ucli.App{
		Name:  "taskflow",
		Usage: "TaskFlow Monitor",
		Flags: []ucli.Flag{
			&ucli.StringFlag{Name: "fixtures-path", Usage: "Path to shared fixtures"},
		},
		Commands: []*ucli.Command{
			{
				Name:  "list",
				Usage: "List jobs",
				Flags: []ucli.Flag{
					&ucli.StringFlag{Name: "status"},
					&ucli.StringFlag{Name: "tag"},
					&ucli.StringFlag{Name: "output", Value: "table"},
				},
				Action: func(ctx *ucli.Context) error {
					jobs, err := core.LoadJobs(core.ResolveFixturesPath(ctx.String("fixtures-path")))
					if err != nil {
						return PrintError(err)
					}
					filtered := core.SortJobs(core.FilterJobs(jobs, ctx.String("status"), ctx.String("tag")))
					if ctx.String("output") == "json" {
						return PrintJSON(filtered)
					}
					PrintMarkerBlock("## BEGIN_JOBS ##", JobsTable(filtered), "## END_JOBS ##")
					return nil
				},
			},
			{
				Name:      "inspect",
				Usage:     "Inspect a job",
				ArgsUsage: "JOB_ID",
				Flags: []ucli.Flag{
					&ucli.StringFlag{Name: "output", Value: "plain"},
				},
				Action: func(ctx *ucli.Context) error {
					jobs, err := core.LoadJobs(core.ResolveFixturesPath(ctx.String("fixtures-path")))
					if err != nil {
						return PrintError(err)
					}
					if ctx.NArg() != 1 {
						return PrintError(fmt.Errorf("expected JOB_ID"))
					}
					job := core.FindJob(jobs, ctx.Args().First())
					if job == nil {
						return PrintError(fmt.Errorf("job not found: %s", ctx.Args().First()))
					}
					if ctx.String("output") == "json" {
						return PrintJSON(job)
					}
					PrintMarkerBlock("## BEGIN_JOB_DETAIL ##", JobPlain(*job), "## END_JOB_DETAIL ##")
					return nil
				},
			},
			{
				Name:  "stats",
				Usage: "Print job stats",
				Flags: []ucli.Flag{
					&ucli.StringFlag{Name: "output", Value: "plain"},
				},
				Action: func(ctx *ucli.Context) error {
					jobs, err := core.LoadJobs(core.ResolveFixturesPath(ctx.String("fixtures-path")))
					if err != nil {
						return PrintError(err)
					}
					stats := core.ComputeStats(jobs)
					if ctx.String("output") == "json" {
						return PrintJSON(stats)
					}
					PrintMarkerBlock("## BEGIN_STATS ##", StatsPlain(stats), "## END_STATS ##")
					return nil
				},
			},
			{
				Name:  "watch",
				Usage: "Watch jobs",
				Flags: []ucli.Flag{
					&ucli.IntFlag{Name: "interval", Value: 5},
					&ucli.BoolFlag{Name: "no-tui"},
				},
				Action: func(ctx *ucli.Context) error {
					root := core.ResolveFixturesPath(ctx.String("fixtures-path"))
					jobs, err := core.LoadJobs(root)
					if err != nil {
						return PrintError(err)
					}
					if ctx.Bool("no-tui") {
						PrintMarkerBlock("## BEGIN_JOBS ##", JobsTable(core.SortJobs(jobs)), "## END_JOBS ##")
						return nil
					}
					events, err := core.LoadEvents(root)
					if err != nil {
						return PrintError(err)
					}
					if _, err := core.LoadConfig(root); err != nil {
						return PrintError(err)
					}
					return tui.Run(jobs, events, ctx.Int("interval"))
				},
			},
		},
	}
}
