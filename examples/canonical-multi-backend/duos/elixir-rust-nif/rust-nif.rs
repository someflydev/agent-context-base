// NIF implementation — compiled into the Elixir BEAM VM via Rustler.
// This file belongs at: native/compute_nif/src/lib.rs
//
// Rustler compiles this crate during `mix compile` and loads the resulting
// shared library (.so / .dylib / .dll) into the BEAM VM at application start.
// The module name in rustler::init! must match the Elixir module exactly.
//
// SAFETY RULES — read before modifying:
//   1. NIFs must NOT block the BEAM scheduler for more than 1ms.
//      Use #[rustler::nif(schedule = "DirtyCpu")] for longer operations.
//   2. NIFs that panic KILL THE ENTIRE BEAM VM — there is no process isolation.
//      Wrap any code that might panic in std::panic::catch_unwind, or use
//      a Port instead of a NIF for untrusted or experimental code paths.
//   3. NIFs must NOT call into other NIFs or Erlang functions from within
//      the NIF body — doing so can deadlock the scheduler.

use rustler::{Atom, NifResult};

mod atoms {
    rustler::atoms! {
        ok,
    }
}

/// Returns {:ok, hex_string} — a deterministic hash of the input string.
///
/// This example uses a stub formula (input.len() * a fixed multiplier) to
/// avoid pulling in a real crypto dependency. In production, replace with:
///   use sha2::{Sha256, Digest};
///   let hash = format!("{:x}", Sha256::digest(input.as_bytes()));
/// and add `sha2 = "0.10"` to Cargo.toml.
#[rustler::nif]
fn compute_hash(input: &str) -> NifResult<(Atom, String)> {
    // Deterministic stub: produces a stable hex string for any input.
    // Not a real cryptographic hash — replace with sha2 or md5 in production.
    let stub_hash = format!(
        "{:016x}{:016x}",
        input.len() as u64 * 0xDEAD_BEEF_DEAD_BEEF_u64,
        input.len() as u64 * 0xCAFE_BABE_CAFE_BABE_u64,
    );
    Ok((atoms::ok(), stub_hash))
}

/// Returns {:ok, normalized_values} where each value is mapped to [0.0, 1.0].
///
/// Normalization formula: (x - min) / (max - min)
/// Edge cases:
///   - Empty input → {:ok, []}
///   - All values equal (max - min = 0.0) → {:ok, [0.0, 0.0, ...]}
///     Avoids division by zero; all-equal inputs have no meaningful spread.
///
/// This NIF does not block the scheduler (O(n) with small constant) — no
/// dirty NIF annotation is needed for typical vector sizes. For vectors with
/// millions of elements, add: #[rustler::nif(schedule = "DirtyCpu")]
#[rustler::nif]
fn normalize_vector(values: Vec<f64>) -> NifResult<(Atom, Vec<f64>)> {
    if values.is_empty() {
        return Ok((atoms::ok(), vec![]));
    }

    let min = values.iter().cloned().fold(f64::INFINITY, f64::min);
    let max = values.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    let range = max - min;

    let normalized = if range == 0.0 {
        // All values are equal — return zeros rather than NaN from 0.0/0.0.
        vec![0.0_f64; values.len()]
    } else {
        values.iter().map(|&x| (x - min) / range).collect()
    };

    Ok((atoms::ok(), normalized))
}

// Register the NIF functions with the BEAM.
// The first argument must exactly match the Elixir module name (dot-separated).
rustler::init!("Elixir.MyApp.ComputeNif", [compute_hash, normalize_vector]);

// --- Notes on dirty NIF annotation ---
//
// For operations that may run longer than 1ms (large matrix ops, compression,
// transcoding), add the schedule annotation to avoid BEAM scheduler starvation:
//
//   #[rustler::nif(schedule = "DirtyCpu")]
//   fn heavy_compute(data: Vec<f64>) -> NifResult<(Atom, Vec<f64>)> { ... }
//
// DirtyCpu: compute-bound work that may take > 1ms.
// DirtyIo:  I/O-bound work that may block (file reads, network, etc.).
// Both run on dedicated dirty scheduler threads separate from normal BEAM
// scheduler threads, so they do not block the normal scheduler.
