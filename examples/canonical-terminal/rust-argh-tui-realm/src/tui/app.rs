use std::io::{self, Stdout};
use std::time::Duration;

use crate::core::models::{Event as JobEvent, Job, JobStatus};
use anyhow::Result;
use crossterm::event::{self, Event, KeyCode, KeyEventKind};
use crossterm::execute;
use crossterm::terminal::{
    disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen,
};
use ratatui::backend::CrosstermBackend;
use ratatui::layout::{Constraint, Direction, Layout};
use ratatui::style::{Color, Modifier, Style};
use ratatui::widgets::{Block, Borders, Cell, Paragraph, Row, Table, Wrap};
use ratatui::Terminal;

enum Message {
    Next,
    Previous,
    ToggleFailed,
    Refresh,
}

struct JobListPanel {
    selected: usize,
    failed_only: bool,
}

impl JobListPanel {
    fn visible_jobs(&self, jobs: &[Job]) -> Vec<Job> {
        jobs.iter()
            .filter(|job| !self.failed_only || job.status.as_str() == "failed")
            .cloned()
            .collect()
    }

    fn update(&mut self, message: &Message, visible_len: usize) {
        match message {
            Message::Next => {
                if visible_len > 0 {
                    self.selected = (self.selected + 1).min(visible_len.saturating_sub(1));
                }
            }
            Message::Previous => self.selected = self.selected.saturating_sub(1),
            Message::ToggleFailed => {
                self.failed_only = !self.failed_only;
                self.selected = 0;
            }
            Message::Refresh => {}
        }
    }
}

struct JobDetailPanel {
    scroll: u16,
}

impl JobDetailPanel {
    fn update(&mut self, message: &Message) {
        if matches!(message, Message::Refresh) {
            self.scroll = 0;
        }
    }
}

pub struct App {
    jobs: Vec<Job>,
    events: Vec<JobEvent>,
    list: JobListPanel,
    detail: JobDetailPanel,
}

impl App {
    fn new(jobs: Vec<Job>, events: Vec<JobEvent>) -> Self {
        Self {
            jobs,
            events,
            list: JobListPanel {
                selected: 0,
                failed_only: false,
            },
            detail: JobDetailPanel { scroll: 0 },
        }
    }

    fn dispatch(&mut self, message: Message) {
        let visible_len = self.list.visible_jobs(&self.jobs).len();
        self.list.update(&message, visible_len);
        self.detail.update(&message);
    }

    fn selected_job(&self) -> Option<Job> {
        self.list
            .visible_jobs(&self.jobs)
            .get(self.list.selected)
            .cloned()
    }
}

struct TerminalGuard;

impl Drop for TerminalGuard {
    fn drop(&mut self) {
        let _ = disable_raw_mode();
        let mut stdout = io::stdout();
        let _ = execute!(stdout, LeaveAlternateScreen);
    }
}

fn setup_terminal() -> Result<Terminal<CrosstermBackend<Stdout>>> {
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen)?;
    Ok(Terminal::new(CrosstermBackend::new(stdout))?)
}

fn status_color(status: &JobStatus) -> Color {
    match status {
        JobStatus::Done => Color::Green,
        JobStatus::Failed => Color::Red,
        JobStatus::Running => Color::Yellow,
        JobStatus::Pending => Color::DarkGray,
    }
}

pub fn run_app(jobs: Vec<Job>, events: Vec<JobEvent>, interval: u64) -> Result<()> {
    let _guard = TerminalGuard;
    let mut terminal = setup_terminal()?;
    let mut app = App::new(jobs, events);

    loop {
        let visible_jobs = app.list.visible_jobs(&app.jobs);
        terminal.draw(|frame| {
            let outer = Layout::default()
                .direction(Direction::Vertical)
                .constraints([Constraint::Length(3), Constraint::Min(10)])
                .split(frame.size());
            let body = Layout::default()
                .direction(Direction::Horizontal)
                .constraints([Constraint::Percentage(58), Constraint::Percentage(42)])
                .split(outer[1]);

            frame.render_widget(
                Paragraph::new(format!(
                    "TaskFlow Monitor | q quit | r refresh | f failed-only={} | poll=component-loop | interval={}s",
                    if app.list.failed_only { "on" } else { "off" },
                    interval
                ))
                .block(Block::default().borders(Borders::ALL).title("Header"))
                .style(Style::default().add_modifier(Modifier::BOLD)),
                outer[0],
            );

            let rows = visible_jobs.iter().enumerate().map(|(idx, job)| {
                let style = if idx == app.list.selected {
                    Style::default().add_modifier(Modifier::REVERSED)
                } else {
                    Style::default().fg(status_color(&job.status))
                };
                Row::new(vec![
                    Cell::from(job.id.clone()),
                    Cell::from(job.name.clone()),
                    Cell::from(job.status.as_str().to_string()),
                    Cell::from(
                        job.duration_s
                            .map(|value| format!("{value:.1}s"))
                            .unwrap_or_else(|| "-".to_string()),
                    ),
                ])
                .style(style)
            });
            frame.render_widget(
                Table::new(
                    rows,
                    [
                        Constraint::Length(10),
                        Constraint::Percentage(48),
                        Constraint::Length(10),
                        Constraint::Length(12),
                    ],
                )
                .header(
                    Row::new(vec!["ID", "NAME", "STATUS", "DURATION"])
                        .style(Style::default().add_modifier(Modifier::BOLD)),
                )
                .block(Block::default().borders(Borders::ALL).title("JobList component")),
                body[0],
            );

            let detail_lines = app
                .selected_job()
                .map(|job| {
                    let mut lines = vec![
                        format!("ID: {}", job.id),
                        format!("Name: {}", job.name),
                        format!("Status: {}", job.status.as_str()),
                        format!(
                            "Started: {}",
                            job.started_at.unwrap_or_else(|| "-".to_string())
                        ),
                        format!(
                            "Duration (s): {}",
                            job.duration_s
                                .map(|value| format!("{value:.1}"))
                                .unwrap_or_else(|| "-".to_string())
                        ),
                        format!("Tags: {}", job.tags.join(", ")),
                        format!("Events loaded: {}", app.events.len()),
                        String::new(),
                        "Output:".to_string(),
                    ];
                    for line in job.output_lines {
                        lines.push(format!("  - {line}"));
                    }
                    lines.join("\n")
                })
                .unwrap_or_else(|| "No jobs available".to_string());
            frame.render_widget(
                Paragraph::new(detail_lines)
                    .block(Block::default().borders(Borders::ALL).title("JobDetail component"))
                    .scroll((app.detail.scroll, 0))
                    .wrap(Wrap { trim: false }),
                body[1],
            );
        })?;

        if event::poll(Duration::from_millis(200))? {
            if let Event::Key(key) = event::read()? {
                if key.kind != KeyEventKind::Press {
                    continue;
                }
                match key.code {
                    KeyCode::Char('q') => break,
                    KeyCode::Down => app.dispatch(Message::Next),
                    KeyCode::Up => app.dispatch(Message::Previous),
                    KeyCode::Char('f') => app.dispatch(Message::ToggleFailed),
                    KeyCode::Char('r') => app.dispatch(Message::Refresh),
                    _ => {}
                }
            }
        }
    }

    Ok(())
}
