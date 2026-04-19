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
            
            # Additional filtering for ignored file parts in path
            full_path = os.path.join(dirpath, f)
            parts = full_path.split(os.sep)
            if any(p in EXAMPLE_SKIP_PATH_PARTS for p in parts):
                continue
            
            # Skip hidden files
            if f.startswith("."):
                continue

            files.append(full_path)
    return files

root_dir = "examples/canonical-analytics/elixir/analytics_workbench/"
files = sorted(get_files(root_dir))

# Catalog entries
catalog_entries = []
for f in files:
    name = os.path.basename(f)
    catalog_entries.append({
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

# Registry entries
registry_entries = []
for f in files:
    # Use path-based name for uniqueness, similar to existing entries if possible
    name = f.replace("examples/canonical-analytics/elixir/analytics_workbench/", "").replace("/", "-").replace(".", "-")
    # remove leading/trailing hyphens if any
    name = name.strip("-")
    
    language = "elixir"
    if f.endswith(".md"): language = "markdown"
    elif f.endswith(".json"): language = "json"
    elif f.endswith(".css"): language = "css"
    elif f.endswith(".js"): language = "javascript"
    elif f.endswith(".heex"): language = "elixir" # phoenix template
    
    registry_entries.append({
        "name": name,
        "path": f,
        "language": language,
        "stack_tags": ["elixir-phoenix"],
        "archetype_tags": ["interactive-data-service"],
        "verification_level": "smoke-verified",
        "confidence": "high"
    })

print("--- CATALOG snipped ---")
print(json.dumps(catalog_entries, indent=2))
print("--- REGISTRY snippet ---")
for entry in registry_entries:
    print(f"  - name: {entry['name']}")
    print(f"    path: {entry['path']}")
    print(f"    language: {entry['language']}")
    print(f"    stack_tags:")
    print(f"      - {entry['stack_tags'][0]}")
    print(f"    archetype_tags:")
    print(f"      - {entry['archetype_tags'][0]}")
    print(f"    verification_level: {entry['verification_level']}")
    print(f"    confidence: {entry['confidence']}")
