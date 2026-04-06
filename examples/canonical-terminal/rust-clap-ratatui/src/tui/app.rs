use std::io::{self, Stdout};
use std::panic;
use std::time::Duration;

use anyhow::Result;
use crossterm::event::{self, Event, KeyCode, KeyEventKind};
use crossterm::execute;
use crossterm::terminal::{
    disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen,
};
use ratatui::backend::CrosstermBackend;
use ratatui::Terminal;

use crate::core::models::{Event as JobEvent, Job};
use crate::tui::state::AppState;
use crate::tui::ui;

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

pub fn run_app(jobs: Vec<Job>, events: Vec<JobEvent>, interval: u64) -> Result<()> {
    let hook = panic::take_hook();
    panic::set_hook(Box::new(move |panic_info| {
        let _ = disable_raw_mode();
        let mut stdout = io::stdout();
        let _ = execute!(stdout, LeaveAlternateScreen);
        hook(panic_info);
    }));

    let _guard = TerminalGuard;
    let mut terminal = setup_terminal()?;
    let mut state = AppState::new(jobs, events);

    loop {
        terminal.draw(|frame| ui::draw(frame, &state, interval))?;
        if event::poll(Duration::from_millis(200))? {
            if let Event::Key(key) = event::read()? {
                if key.kind != KeyEventKind::Press {
                    continue;
                }
                match key.code {
                    KeyCode::Char('q') => break,
                    KeyCode::Char('r') => state.scroll = 0,
                    KeyCode::Char('f') => state.toggle_filter(),
                    KeyCode::Down => state.next(),
                    KeyCode::Up => state.previous(),
                    KeyCode::PageDown => state.scroll = state.scroll.saturating_add(5),
                    KeyCode::PageUp => state.scroll = state.scroll.saturating_sub(5),
                    _ => {}
                }
            }
        }
    }

    Ok(())
}
