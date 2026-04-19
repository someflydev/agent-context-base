import os
import json

EXAMPLE_SUPPORT_FILENAMES = {
    "README.md", "catalog.json", "Dockerfile", "build.properties", "build.sbt",
    "build.gradle.kts", "build.zig", "build.zig.zon", "shard.yml", "requirements.txt",
    "settings.gradle.kts", "go.mod", "go.sum", "Cargo.toml", "Cargo.lock",
    "Gemfile", "config.ru", "mix.exs", "mix.lock", "docker-compose.yml",
}

EXAMPLE_SKIP_PATH_PARTS = {
    "__pycache__", "_build", "deps", "node_modules", "target", "build",
    ".dart_tool", "zig-cache", "zig-out", "nimcache", "vendor", ".git",
}

def get_files(root):
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip directories in EXAMPLE_SKIP_PATH_PARTS
        dirnames[:] = [d for d in dirnames if d not in EXAMPLE_SKIP_PATH_PARTS]
        
        for f in filenames:
            if f in EXAMPLE_SUPPORT_FILENAMES:
                continue
            
            full_path = os.path.join(dirpath, f)
            parts = full_path.split(os.sep)
            if any(p in EXAMPLE_SKIP_PATH_PARTS for p in parts):
                continue
            
            if f.startswith("."):
                continue

            files.append(full_path)
    return sorted(files)

root_dir = "examples/canonical-analytics/elixir/analytics_workbench/"
new_files = get_files(root_dir)

# Update catalog.json
catalog_path = "examples/catalog.json"
with open(catalog_path, "r", encoding="utf-8") as f:
    catalog_data = json.load(f)

for f in new_files:
    name = os.path.basename(f)
    catalog_data["entries"].append({
        "path": f,
        "category": "analytics",
        "summary": f"Elixir analytics workbench component: {name}",
        "stacks": ["elixir-phoenix"],
        "archetypes": ["interactive-data-service"],
        "workflows": ["implement-canonical-analytics"],
        "patterns": ["server-rendered-viz", "htmx", "plotly", "utility-first-css"],
        "rank": 80,
        "stability": "verified-runtime"
    })

with open(catalog_path, "w", encoding="utf-8") as f:
    json.dump(catalog_data, f, indent=2)

# Update example_registry.yaml
registry_path = "verification/example_registry.yaml"

with open(registry_path, "a", encoding="utf-8") as f:
    for f_path in new_files:
        name = f_path.replace("examples/canonical-analytics/elixir/analytics_workbench/", "").replace("/", "-").replace(".", "-")
        name = name.strip("-")
        
        language = "elixir"
        if f_path.endswith(".md"): language = "markdown"
        elif f_path.endswith(".json"): language = "json"
        elif f_path.endswith(".css"): language = "css"
        elif f_path.endswith(".js"): language = "javascript"
        elif f_path.endswith(".heex"): language = "elixir"
        
        f.write(f"  - name: {name}\n")
        f.write(f"    path: {f_path}\n")
        f.write(f"    language: {language}\n")
        f.write(f"    stack_tags:\n")
        f.write(f"      - elixir-phoenix\n")
        f.write(f"    archetype_tags:\n")
        f.write(f"      - interactive-data-service\n")
        f.write(f"    verification_level: smoke-verified\n")
        f.write(f"    confidence: high\n")

print(f"Updated {catalog_path} and {registry_path} with {len(new_files)} new entries.")
