defmodule TenantCore.Distributions do
  def weighted_plan(seed_state) do
    choices = [{"free", 50}, {"pro", 35}, {"enterprise", 15}]
    weighted_pick(choices, seed_state)
  end

  def weighted_region(seed_state) do
    choices = [{"us-east", 40}, {"us-west", 30}, {"eu-west", 20}, {"ap-southeast", 10}]
    weighted_pick(choices, seed_state)
  end

  def weighted_role(seed_state) do
    choices = [{"owner", 5}, {"admin", 10}, {"member", 60}, {"viewer", 25}]
    weighted_pick(choices, seed_state)
  end

  def weighted_project_status(seed_state) do
    choices = [{"active", 60}, {"archived", 25}, {"draft", 15}]
    weighted_pick(choices, seed_state)
  end

  def weighted_action(seed_state) do
    choices = [{"created", 10}, {"updated", 40}, {"deleted", 5}, {"archived", 5}, {"invited", 20}, {"exported", 20}]
    weighted_pick(choices, seed_state)
  end

  def weighted_resource_type(seed_state) do
    choices = [{"project", 40}, {"user", 10}, {"membership", 20}, {"api_key", 10}, {"invitation", 20}]
    weighted_pick(choices, seed_state)
  end

  def weighted_locale(seed_state) do
    choices = [{"en-US", 60}, {"en-GB", 20}, {"fr-FR", 10}, {"de-DE", 10}]
    weighted_pick(choices, seed_state)
  end

  def timezone_for_locale(locale) do
    case locale do
      "en-US" -> "America/New_York"
      "en-GB" -> "Europe/London"
      "fr-FR" -> "Europe/Paris"
      "de-DE" -> "Europe/Berlin"
      _ -> "UTC"
    end
  end

  defp weighted_pick(weighted_list, _seed_state) do
    total = Enum.sum(Enum.map(weighted_list, fn {_, w} -> w end))
    target = :rand.uniform(total)
    Enum.reduce_while(weighted_list, 0, fn {value, weight}, acc ->
      new_acc = acc + weight
      if new_acc >= target, do: {:halt, value}, else: {:cont, new_acc}
    end)
  end
end
