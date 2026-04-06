use ratatui::layout::{Constraint, Direction, Layout};
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, Cell, Paragraph, Row, Table, Wrap};
use ratatui::Frame;

use crate::core::models::{Job, JobStatus};
use crate::tui::state::AppState;

fn status_style(status: &JobStatus) -> Style {
    match status {
        JobStatus::Done => Style::default().fg(Color::Green),
        JobStatus::Failed => Style::default().fg(Color::Red),
        JobStatus::Running => Style::default().fg(Color::Yellow),
        JobStatus::Pending => Style::default().fg(Color::DarkGray),
    }
}

fn detail_lines(job: &Job, events: usize) -> Vec<Line<'static>> {
    let mut lines = vec![
        Line::from(format!("ID: {}", job.id)),
        Line::from(format!("Name: {}", job.name)),
        Line::from(Span::styled(
            format!("Status: {}", job.status.as_str()),
            status_style(&job.status),
        )),
        Line::from(format!(
            "Started: {}",
            job.started_at.clone().unwrap_or_else(|| "-".to_string())
        )),
        Line::from(format!(
            "Duration (s): {}",
            job.duration_s
                .map(|value| format!("{value:.1}"))
                .unwrap_or_else(|| "-".to_string())
        )),
        Line::from(format!("Tags: {}", job.tags.join(", "))),
        Line::from(format!("Events loaded: {events}")),
        Line::from(""),
        Line::from("Output:"),
    ];
    for line in &job.output_lines {
        lines.push(Line::from(format!("  - {line}")));
    }
    lines
}

pub fn draw(frame: &mut Frame, state: &AppState, interval: u64) {
    let layout = Layout::default()
        .direction(Direction::Vertical)
        .constraints([Constraint::Length(3), Constraint::Min(10)])
        .split(frame.size());
    let body = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Percentage(58), Constraint::Percentage(42)])
        .split(layout[1]);

    let header = Paragraph::new(format!(
        "TaskFlow Monitor | q quit | r refresh | f failed filter={} | interval={}s",
        if state.filter_failed_only {
            "on"
        } else {
            "off"
        },
        interval
    ))
    .block(Block::default().borders(Borders::ALL).title("Header"))
    .style(Style::default().add_modifier(Modifier::BOLD));
    frame.render_widget(header, layout[0]);

    let visible_jobs = state.visible_jobs();
    let rows = visible_jobs.iter().enumerate().map(|(idx, job)| {
        let style = if idx == state.selected {
            Style::default().add_modifier(Modifier::REVERSED)
        } else {
            status_style(&job.status)
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
    let table = Table::new(
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
    .block(Block::default().borders(Borders::ALL).title("Jobs"));
    frame.render_widget(table, body[0]);

    let detail_text = state
        .selected_job()
        .map(|job| detail_lines(&job, state.events.len()))
        .unwrap_or_else(|| vec![Line::from("No jobs available")]);
    let detail = Paragraph::new(detail_text)
        .block(Block::default().borders(Borders::ALL).title("Detail"))
        .scroll((state.scroll, 0))
        .wrap(Wrap { trim: false });
    frame.render_widget(detail, body[1]);
}
