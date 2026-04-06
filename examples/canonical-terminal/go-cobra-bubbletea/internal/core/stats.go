package core

import "math"

func ComputeStats(jobs []Job) Stats {
	byStatus := map[string]int{
		string(StatusPending): 0,
		string(StatusRunning): 0,
		string(StatusDone):    0,
		string(StatusFailed):  0,
	}
	var durations []float64
	for _, job := range jobs {
		byStatus[string(job.Status)]++
		if job.DurationS != nil {
			durations = append(durations, *job.DurationS)
		}
	}
	avg := 0.0
	if len(durations) > 0 {
		sum := 0.0
		for _, value := range durations {
			sum += value
		}
		avg = math.Round(sum/float64(len(durations))*100) / 100
	}
	failureRate := 0.0
	if len(jobs) > 0 {
		failureRate = math.Round(float64(byStatus[string(StatusFailed)])/float64(len(jobs))*100) / 100
	}
	return Stats{
		Total:        len(jobs),
		ByStatus:     byStatus,
		AvgDurationS: avg,
		FailureRate:  failureRate,
	}
}
