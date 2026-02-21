#!/usr/bin/env python3
"""Generate Paprika 3 import files (.paprikarecipes and .yml)."""

import gzip
import hashlib
import json
import uuid
import zipfile
import sys
from pathlib import Path

ICLOUD = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs"


def make_recipe_json(
    name,
    ingredients,
    directions,
    *,
    servings="",
    prep_time="",
    cook_time="",
    total_time="",
    source="",
    source_url="",
    categories=None,
    notes="",
    description="",
    nutritional_info="",
    difficulty="",
    rating=0,
    on_favorites=False,
):
    """Build a Paprika recipe dict with proper field names and types."""
    uid = str(uuid.uuid4()).upper()
    recipe = {
        "uid": uid,
        "name": name,
        "ingredients": ingredients,
        "directions": directions,
        "description": description,
        "notes": notes,
        "servings": servings,
        "prep_time": prep_time,
        "cook_time": cook_time,
        "total_time": total_time,
        "source": source,
        "source_url": source_url,
        "nutritional_info": nutritional_info,
        "difficulty": difficulty,
        "rating": rating,
        "on_favorites": on_favorites,
        "categories": categories or [],
        "created": "",
        "image_url": None,
        "photo_hash": None,
        "photo": None,
        "photo_large": None,
        "photo_url": None,
        "scale": None,
        "deleted": False,
        "in_trash": False,
        "is_pinned": False,
        "on_grocery_list": None,
    }
    # Paprika uses a sha256 hash of the recipe fields
    fields_for_hash = {k: v for k, v in recipe.items() if k != "hash"}
    recipe["hash"] = hashlib.sha256(
        json.dumps(fields_for_hash, sort_keys=True).encode()
    ).hexdigest()
    return recipe


def write_paprikarecipes(recipes, output_path):
    """Write a .paprikarecipes file (zip of gzipped JSON)."""
    output_path = Path(output_path)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_STORED) as zf:
        for recipe in recipes:
            # Each recipe is a gzipped JSON, stored as <name>.paprikarecipe
            data = json.dumps(recipe, ensure_ascii=False).encode("utf-8")
            compressed = gzip.compress(data)
            safe_name = recipe["name"].replace("/", "-").replace("\\", "-")
            zf.writestr(f"{safe_name}.paprikarecipe", compressed)
    print(f"Wrote {output_path} ({len(recipes)} recipe(s))")


def write_yaml(recipes, output_path):
    """Write a .yml file in Paprika's expected YAML format."""
    output_path = Path(output_path)
    lines = []
    for i, r in enumerate(recipes):
        prefix = "- " if len(recipes) > 1 else ""
        indent = "  " if len(recipes) > 1 else ""
        lines.append(f"{prefix}name: {r['name']}")
        if r.get("servings"):
            lines.append(f"{indent}servings: {r['servings']}")
        if r.get("source"):
            lines.append(f"{indent}source: {r['source']}")
        if r.get("source_url"):
            lines.append(f"{indent}source_url: {r['source_url']}")
        if r.get("prep_time"):
            lines.append(f"{indent}prep_time: {r['prep_time']}")
        if r.get("cook_time"):
            lines.append(f"{indent}cook_time: {r['cook_time']}")
        if r.get("total_time"):
            lines.append(f"{indent}total_time: {r['total_time']}")
        if r.get("difficulty"):
            lines.append(f"{indent}difficulty: {r['difficulty']}")
        if r.get("rating"):
            lines.append(f"{indent}rating: {r['rating']}")
        if r.get("on_favorites"):
            lines.append(f"{indent}on_favorites: yes")
        if r.get("categories"):
            cats = ", ".join(r["categories"])
            lines.append(f"{indent}categories: [{cats}]")
        if r.get("nutritional_info"):
            lines.append(f"{indent}nutritional_info: {r['nutritional_info']}")
        if r.get("description"):
            lines.append(f"{indent}description: |")
            for line in r["description"].split("\n"):
                lines.append(f"{indent}  {line}")
        if r.get("notes"):
            lines.append(f"{indent}notes: |")
            for line in r["notes"].split("\n"):
                lines.append(f"{indent}  {line}")
        lines.append(f"{indent}ingredients: |")
        for line in r["ingredients"].split("\n"):
            lines.append(f"{indent}  {line}")
        lines.append(f"{indent}directions: |")
        for line in r["directions"].split("\n"):
            lines.append(f"{indent}  {line}")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {output_path} ({len(recipes)} recipe(s))")


# --- Test recipe ---
if __name__ == "__main__":
    test_recipe = make_recipe_json(
        name="Testrecept - Enkel Pasta",
        ingredients="400 g pasta\n2 msk olivolja\n2 vitlöksklyftor, hackade\n1 burk krossade tomater (400 g)\n1 tsk salt\nNymald svartpeppar\nFärsk basilika",
        directions="1. Koka pastan enligt förpackningen.\n2. Hetta upp olivolja i en stekpanna. Fräs vitlöken 1 minut.\n3. Tillsätt krossade tomater, salt och peppar. Låt sjuda 10 minuter.\n4. Blanda pastan med såsen. Toppa med basilika.",
        servings="4 portioner",
        prep_time="5 min",
        cook_time="15 min",
        categories=["Middag", "Snabbt", "Pasta"],
        notes="Importtest via Claude",
        source="Claude",
    )

    dest = ICLOUD / "Paprika Import"
    dest.mkdir(exist_ok=True)

    write_paprikarecipes([test_recipe], dest / "test_import.paprikarecipes")
    write_yaml([test_recipe], dest / "test_import.yml")

    print(f"\nFiles in: {dest}")
    print("On iPhone: Open Files → iCloud Drive → Paprika Import")
    print("  .paprikarecipes: Tap to open directly in Paprika")
    print("  .yml: Use Paprika → Settings → Import Recipes")
