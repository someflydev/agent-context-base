# This is an in-process seam example — no docker-compose.
# Rust compiles into the Elixir BEAM VM as a native implemented function (NIF)
# via Rustler. There is no separate Rust container or network boundary.
# See seam.md for mix.exs setup, Rustler configuration, and build instructions.
#
# Dependencies (mix.exs):
#   {:rustler, "~> 0.31", runtime: false}

defmodule MyApp.ComputeNif do
  @moduledoc """
  NIF host module for the compute_nif Rust crate.

  Rustler replaces the stub implementations below with the compiled Rust NIF
  at application startup. If the NIF library fails to load, calls will raise
  :nif_not_loaded — check that `mix compile` completed successfully and that
  the Rust toolchain is installed.

  Seam contract:
    - compute_hash/1 — returns {:ok, hex_string} for any binary input
    - normalize_vector/1 — returns {:ok, [float]} with values in [0.0, 1.0];
      returns {:ok, []} for empty input; returns {:ok, [0.0, ...]} if all
      values are equal (max - min = 0.0)

  See seam.md for: NIF vs Port trade-off, dirty NIF annotation, safety rules.
  """

  use Rustler, otp_app: :my_app, crate: "compute_nif"

  # Stubs — replaced at runtime by the compiled Rust NIF.
  # :erlang.nif_error/1 raises if the NIF library is not loaded.
  @doc "Returns {:ok, hex_string} — a deterministic hash of the input string."
  def compute_hash(_input), do: :erlang.nif_error(:nif_not_loaded)

  @doc "Returns {:ok, normalized_values} — each value mapped to [0.0, 1.0]."
  def normalize_vector(_values), do: :erlang.nif_error(:nif_not_loaded)
end

# --- Usage examples (for IEx or tests) ---
#
# Calling compute_hash:
#   iex> MyApp.ComputeNif.compute_hash("hello world")
#   {:ok, "b6a4f9d2deadbeef..."}   # deterministic stub hash
#
# Calling normalize_vector:
#   iex> MyApp.ComputeNif.normalize_vector([1.0, 2.0, 3.0])
#   {:ok, [0.0, 0.5, 1.0]}
#
#   iex> MyApp.ComputeNif.normalize_vector([5.0, 5.0, 5.0])
#   {:ok, [0.0, 0.0, 0.0]}   # all equal → zeros (max - min = 0.0)
#
#   iex> MyApp.ComputeNif.normalize_vector([])
#   {:ok, []}

# --- Port alternative (for unsafe or potentially-panicking code) ---
#
# If the Rust code might panic, block the BEAM scheduler, or interact with
# unsafe external state, use a Port instead of a NIF. A NIF panic kills the
# entire BEAM VM; a Port crash is isolated to the OS process and the Elixir
# supervisor can restart it.
#
# defmodule MyApp.ComputePort do
#   def start(binary_path) do
#     Port.open({:spawn_executable, binary_path}, [
#       :binary,
#       :exit_status,
#       {:packet, 4}   # 4-byte length-prefix framing
#     ])
#   end
#
#   def call(port, payload) do
#     encoded = :erlang.term_to_binary(payload)
#     send(port, {self(), {:command, encoded}})
#     receive do
#       {^port, {:data, data}} -> :erlang.binary_to_term(data)
#     after
#       5_000 -> {:error, :timeout}
#     end
#   end
# end
#
# The Rust binary reads from stdin and writes to stdout using the same
# 4-byte length-prefix framing. See seam.md for the Port setup details.
