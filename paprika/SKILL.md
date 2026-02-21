---
name: paprika
description: Export recipes to Paprika 3 format. Triggers on "recipe", "paprika", "export recipe", "save recipe", "matrecept", "recept".
---

# Paprika 3 Recipe Export

Export recipes as `.paprikarecipes` files for direct import into Paprika 3.

## How It Works

The export script at `scripts/paprika_export.py` generates `.paprikarecipes` files (zip of gzipped JSON — the native Paprika import format).

## Workflow

1. Build recipe data using `make_recipe_json()`
2. Export with `write_paprikarecipes()`
3. File lands in iCloud Drive for easy access on iPhone

## Script Usage

```python
import sys
sys.path.insert(0, "/Users/tim/dev/claude-skills/paprika/scripts")
from paprika_export import make_recipe_json, write_paprikarecipes

ICLOUD = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs"
dest = ICLOUD / "Paprika Import"
dest.mkdir(exist_ok=True)

recipe = make_recipe_json(
    name="Recipe Name",
    ingredients="200 g flour\n2 eggs\n1 dl milk",
    directions="1. Mix dry ingredients.\n2. Add eggs and milk.\n3. Cook.",
    servings="4",
    prep_time="10 min",
    cook_time="20 min",
    categories=["Dinner", "Quick"],
    source="Claude",
    notes="Optional notes",
)

write_paprikarecipes([recipe], dest / "recipe_name.paprikarecipes")
```

## Required Fields

| Field | Type | Description |
|---|---|---|
| `name` | str | Recipe title |
| `ingredients` | str | Newline-separated, one per line |
| `directions` | str | Newline-separated steps |

## Optional Fields

| Field | Type | Default |
|---|---|---|
| `servings` | str | "" |
| `prep_time` | str | "" |
| `cook_time` | str | "" |
| `total_time` | str | "" |
| `source` | str | "" |
| `source_url` | str | "" |
| `categories` | list[str] | [] |
| `notes` | str | "" |
| `description` | str | "" |
| `difficulty` | str | "" |
| `rating` | int | 0 |

## Output

- **Path**: `~/Library/Mobile Documents/com~apple~CloudDocs/Paprika Import/`
- **Format**: `.paprikarecipes` (tap to open in Paprika on iPhone)
- **Multiple recipes**: Pass a list to `write_paprikarecipes()` for batch export

## Important

- `ingredients`: One ingredient per line, include quantities
- `directions`: Number the steps for clarity
- `categories`: Use these to organize in Paprika (e.g., "Middag", "Snabbt", "Vegetariskt")
- Always set `source="Claude"` when generating recipes
- File names should be descriptive and safe (no special chars)
