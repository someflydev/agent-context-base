import blessed from "blessed";

import { loadConfig, loadJobs } from "../core/loader.js";
import { computeStats } from "../core/stats.js";
import type { Job } from "../core/models.js";

function renderJobDetail(job: Job | undefined): string {
  if (!job) {
    return "No job selected.";
  }
  return [
    job.name,
    `ID: ${job.id}`,
    `Status: ${job.status}`,
    `Started: ${job.started_at ?? "-"}`,
    `Duration: ${job.duration_s ?? "-"}s`,
    `Tags: ${job.tags.join(", ")}`,
    "",
    "Output:",
    ...job.output_lines.map((line) => `- ${line}`),
  ].join("\n");
}

export async function runTui(fixturesPath: string): Promise<void> {
  if (!process.stdout.isTTY) {
    return;
  }

  let jobs = await loadJobs(fixturesPath);
  let selectedIndex = 0;
  const config = await loadConfig(fixturesPath);

  const screen = blessed.screen({ smartCSR: true, title: "TaskFlow Monitor" });
  const statusBar = blessed.text({ parent: screen, top: 0, left: 0, width: "100%", height: 1, tags: false });
  const jobList = blessed.list({
    parent: screen,
    top: 1,
    left: 0,
    width: "55%",
    height: "90%",
    keys: true,
    border: "line",
    label: " Jobs ",
    style: { selected: { inverse: true } },
  });
  const detail = blessed.box({
    parent: screen,
    top: 1,
    left: "55%",
    width: "45%",
    height: "90%",
    border: "line",
    label: " Detail ",
    scrollable: true,
    alwaysScroll: true,
  });
  const help = blessed.text({
    parent: screen,
    bottom: 0,
    left: 0,
    width: "100%",
    height: 1,
    content: "Keys: q quit | r refresh | arrows navigate",
  });
  void help;

  async function refresh(): Promise<void> {
    jobs = await loadJobs(fixturesPath);
    const stats = computeStats(jobs);
    statusBar.setContent(
      `Queue ${config.queue_name} | total ${stats.total} | done ${stats.by_status.done} | failed ${stats.by_status.failed} | running ${stats.by_status.running} | pending ${stats.by_status.pending}`,
    );
    jobList.setItems(jobs.map((job) => `${job.id} ${job.name} [${job.status}]`));
    jobList.select(selectedIndex);
    detail.setContent(renderJobDetail(jobs[selectedIndex]));
    screen.render();
  }

  jobList.on("select item", (_, index) => {
    selectedIndex = index;
    detail.setContent(renderJobDetail(jobs[selectedIndex]));
    screen.render();
  });
  jobList.on("keypress", (_, key) => {
    if (key.name === "up") {
      selectedIndex = Math.max(selectedIndex - 1, 0);
    }
    if (key.name === "down") {
      selectedIndex = Math.min(selectedIndex + 1, Math.max(jobs.length - 1, 0));
    }
    detail.setContent(renderJobDetail(jobs[selectedIndex]));
  });

  screen.key(["q", "C-c"], () => {
    screen.destroy();
  });
  screen.key(["r"], () => {
    void refresh();
  });
  screen.key(["f"], () => {
    const failedOnly = jobs.filter((job) => job.status === "failed");
    if (failedOnly.length > 0) {
      jobs = failedOnly;
      selectedIndex = 0;
      void refresh();
    }
  });

  await refresh();
  jobList.focus();
}
