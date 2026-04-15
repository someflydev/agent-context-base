import os
from pathlib import Path
import unittest

class TestPlotlyHTMXVizDoctrine(unittest.TestCase):
    def setUp(self):
        self.path = Path("context/doctrine/plotly-htmx-server-rendered-viz.md")
        self.assertTrue(self.path.exists(), "Doctrine file missing")
        self.text = self.path.read_text(encoding="utf-8")

    def test_doctrine_file_exists(self):
        pass # tested in setUp

    def test_doctrine_has_rules_1_through_11(self):
        for i in range(1, 12):
            self.assertIn(f"Rule {i}", self.text)

    def test_doctrine_references_backend_driven_ui_correctness(self):
        self.assertIn("backend-driven-ui-correctness.md", self.text)

    def test_doctrine_references_chart_type_selection_skill(self):
        self.assertIn("context/skills/chart-type-selection.md", self.text)

    def test_doctrine_references_filter_panel_rendering_rules(self):
        self.assertIn("filter-panel-rendering-rules.md", self.text)

class TestTailwindDoctrine(unittest.TestCase):
    def setUp(self):
        self.path = Path("context/doctrine/tailwind-utility-first.md")
        self.assertTrue(self.path.exists(), "Doctrine file missing")
        self.text = self.path.read_text(encoding="utf-8")

    def test_doctrine_file_exists(self):
        pass

    def test_doctrine_has_rules_1_through_6(self):
        for i in range(1, 7):
            self.assertIn(f"Rule {i}", self.text)

    def test_doctrine_references_filter_panel_rendering_rules(self):
        self.assertIn("filter-panel-rendering-rules.md", self.text)

class TestAnalyticsWorkbenchArchetype(unittest.TestCase):
    def setUp(self):
        self.path = Path("context/archetypes/analytics-workbench.md")
        self.assertTrue(self.path.exists(), "Archetype file missing")
        self.text = self.path.read_text(encoding="utf-8")

    def test_archetype_file_exists(self):
        pass

    def test_archetype_references_all_four_stacks(self):
        self.assertIn("python-fastapi-jinja2-htmx-plotly.md", self.text)
        self.assertIn("go-echo-templ-htmx-plotly.md", self.text)
        self.assertIn("rust-axum-askama-htmx-plotly.md", self.text)
        self.assertIn("elixir-phoenix-htmx-plotly.md", self.text)

    def test_archetype_references_visualization_workflow(self):
        self.assertIn("add-visualization-panel.md", self.text)

    def test_archetype_references_visualization_doctrine(self):
        self.assertIn("plotly-htmx-server-rendered-viz.md", self.text)

    def test_archetype_references_tailwind_doctrine(self):
        self.assertIn("tailwind-utility-first.md", self.text)

class TestPlotlyHTMXArcStacks(unittest.TestCase):
    def test_python_stack_file_exists(self):
        self.assertTrue(Path("context/stacks/python-fastapi-jinja2-htmx-plotly.md").exists())
    
    def test_go_stack_file_exists(self):
        self.assertTrue(Path("context/stacks/go-echo-templ-htmx-plotly.md").exists())
    
    def test_rust_stack_file_exists(self):
        self.assertTrue(Path("context/stacks/rust-axum-askama-htmx-plotly.md").exists())
    
    def test_elixir_stack_file_exists(self):
        self.assertTrue(Path("context/stacks/elixir-phoenix-htmx-plotly.md").exists())

    def test_python_stack_has_figure_builder_section(self):
        text = Path("context/stacks/python-fastapi-jinja2-htmx-plotly.md").read_text(encoding="utf-8")
        self.assertIn("## Figure Builder Pattern", text)
        
    def test_go_stack_has_figure_builder_section(self):
        text = Path("context/stacks/go-echo-templ-htmx-plotly.md").read_text(encoding="utf-8")
        self.assertIn("## Figure Builder Pattern", text)

    def test_rust_stack_has_figure_builder_section(self):
        text = Path("context/stacks/rust-axum-askama-htmx-plotly.md").read_text(encoding="utf-8")
        self.assertIn("## Figure Builder Pattern", text)

    def test_elixir_stack_has_figure_builder_section(self):
        text = Path("context/stacks/elixir-phoenix-htmx-plotly.md").read_text(encoding="utf-8")
        self.assertIn("## Figure Builder Pattern", text)

    def test_elixir_stack_mentions_htmx_over_liveview(self):
        text = Path("context/stacks/elixir-phoenix-htmx-plotly.md").read_text(encoding="utf-8")
        self.assertIn("HTMX over LiveView", text)

class TestPlotlyHTMXArcSkills(unittest.TestCase):
    def test_chart_type_selection_exists(self):
        self.assertTrue(Path("context/skills/chart-type-selection.md").exists())
    
    def test_chart_type_selection_has_task_table(self):
        text = Path("context/skills/chart-type-selection.md").read_text(encoding="utf-8")
        self.assertIn("Task-to-Chart Family Table", text)

    def test_chart_type_selection_has_anti_patterns_section(self):
        text = Path("context/skills/chart-type-selection.md").read_text(encoding="utf-8")
        self.assertIn("## Anti-Patterns", text)

    def test_figure_builder_design_exists(self):
        self.assertTrue(Path("context/skills/plotly-figure-builder-design.md").exists())
        
    def test_figure_builder_design_has_three_layer_model(self):
        text = Path("context/skills/plotly-figure-builder-design.md").read_text(encoding="utf-8")
        self.assertIn("## The Three-Layer Model", text)

    def test_figure_builder_design_has_language_notes_for_all_four_stacks(self):
        text = Path("context/skills/plotly-figure-builder-design.md").read_text(encoding="utf-8")
        self.assertIn("Python:", text)
        self.assertIn("Go:", text)
        self.assertIn("Rust:", text)
        self.assertIn("Elixir:", text)

class TestPlotlyHTMXArcWorkflow(unittest.TestCase):
    def setUp(self):
        self.path = Path("context/workflows/add-visualization-panel.md")
        self.assertTrue(self.path.exists(), "Workflow file missing")
        self.text = self.path.read_text(encoding="utf-8")

    def test_workflow_file_exists(self):
        pass

    def test_workflow_has_chart_type_selection_step(self):
        self.assertIn("Select chart type", self.text)

    def test_workflow_has_smoke_test_step(self):
        self.assertIn("Add smoke test", self.text)

    def test_workflow_references_tailwind_doctrine(self):
        self.assertIn("tailwind-utility-first.md", self.text)

    def test_workflow_references_filter_panel_rendering_rules(self):
        self.assertIn("filter-panel-rendering-rules.md", self.text)

class TestPlotlyHTMXArcRouterUpdates(unittest.TestCase):
    def test_task_router_references_chart_type_selection(self):
        text = Path("context/router/task-router.md").read_text(encoding="utf-8")
        self.assertIn("context/skills/chart-type-selection.md", text)
    
    def test_task_router_references_add_visualization_panel(self):
        text = Path("context/router/task-router.md").read_text(encoding="utf-8")
        self.assertIn("context/workflows/add-visualization-panel.md", text)

    def test_task_router_references_tailwind_doctrine(self):
        text = Path("context/router/task-router.md").read_text(encoding="utf-8")
        self.assertIn("context/doctrine/tailwind-utility-first.md", text)

    def test_stack_router_references_python_jinja2_plotly_stack(self):
        text = Path("context/router/stack-router.md").read_text(encoding="utf-8")
        self.assertIn("python-fastapi-jinja2-htmx-plotly.md", text)
        
    def test_stack_router_references_go_echo_templ_plotly_stack(self):
        text = Path("context/router/stack-router.md").read_text(encoding="utf-8")
        self.assertIn("go-echo-templ-htmx-plotly.md", text)
        
    def test_stack_router_references_rust_axum_askama_plotly_stack(self):
        text = Path("context/router/stack-router.md").read_text(encoding="utf-8")
        self.assertIn("rust-axum-askama-htmx-plotly.md", text)
        
    def test_stack_router_references_elixir_phoenix_htmx_plotly_stack(self):
        text = Path("context/router/stack-router.md").read_text(encoding="utf-8")
        self.assertIn("elixir-phoenix-htmx-plotly.md", text)

    def test_archetype_router_references_analytics_workbench(self):
        text = Path("context/router/archetype-router.md").read_text(encoding="utf-8")
        self.assertIn("analytics-workbench.md", text)

    def test_alias_catalog_references_analytics_workbench(self):
        text = Path("context/router/alias-catalog.yaml").read_text(encoding="utf-8")
        self.assertIn("context/archetypes/analytics-workbench.md", text)

class TestAgentMdDogfoodingSection(unittest.TestCase):
    def test_agent_md_has_dogfooding_section(self):
        text = Path("AGENT.md").read_text(encoding="utf-8")
        self.assertIn("## Dogfooding Repo Artifacts", text)

    def test_agent_md_dogfooding_references_canonical_faker(self):
        text = Path("AGENT.md").read_text(encoding="utf-8")
        self.assertIn("examples/canonical-faker/", text)

if __name__ == "__main__":
    unittest.main()