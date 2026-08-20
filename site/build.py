#!/usr/bin/env python3
"""
Site builder for sanjay-bhandari.com.np

Usage:
    python3 build.py

Content structure:

    content/
    ├── site.json
    ├── profile.json
    ├── cv.json
    ├── projects/
    │   ├── hermes-atc.json
    │   └── ...
    └── research/
        ├── energy-efficient-multi-hop-v1.json
        └── ...

To add a project:
    1. Create content/projects/<slug>.json
    2. Re-run this script.

To add research:
    1. Create content/research/<slug>.json
    2. Re-run this script.

The build regenerates dist/ from scratch every run.
"""

import json
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------

ROOT = Path(__file__).parent.resolve()

CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
DIST = ROOT / "dist"

PROJECTS_DIR = CONTENT / "projects"
RESEARCH_DIR = CONTENT / "research"


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

TIER_ORDER = {
    "S": 0,
    "A": 1,
    "B": 2,
    "micro": 3,
}


# ---------------------------------------------------------------------------
# CONTENT LOADERS
# ---------------------------------------------------------------------------

def load(name):
    """
    Load a JSON file directly from content/.
    """
    path = CONTENT / name

    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_projects():
    """
    Load all project JSON files from content/projects/.

    Projects are sorted by tier first, then title.
    """

    projects = []

    if not PROJECTS_DIR.exists():
        return projects

    for path in sorted(PROJECTS_DIR.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            projects.append(json.load(f))

    projects.sort(
        key=lambda p: (
            TIER_ORDER.get(p.get("tier", "B"), 9),
            p["title"],
        )
    )

    return projects


def load_research():
    """
    Load all research JSON files from content/research/.

    Research is sorted newest-first by date.
    """

    research = []

    if not RESEARCH_DIR.exists():
        return research

    for path in sorted(RESEARCH_DIR.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            research.append(json.load(f))

    research.sort(
        key=lambda r: r.get("date", ""),
        reverse=True,
    )

    return research


# ---------------------------------------------------------------------------
# BUILD
# ---------------------------------------------------------------------------

def main():

    print("\nBuilding Sanjay Bhandari Engineering Archive...\n")

    # -----------------------------------------------------------------------
    # Clean previous build
    # -----------------------------------------------------------------------

    if DIST.exists():
        shutil.rmtree(DIST)

    DIST.mkdir(parents=True)

    # -----------------------------------------------------------------------
    # Copy static assets
    # -----------------------------------------------------------------------

    if STATIC.exists():
        shutil.copytree(STATIC, DIST / "static")

    # -----------------------------------------------------------------------
    # Jinja environment
    # -----------------------------------------------------------------------

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # -----------------------------------------------------------------------
    # Load content
    # -----------------------------------------------------------------------

    site = load("site.json")
    profile = load("profile.json")
    cv = load("cv.json")

    projects = load_projects()
    research_items = load_research()

    # -----------------------------------------------------------------------
    # Derived data
    # -----------------------------------------------------------------------

    all_tags = sorted(
        {
            tag
            for project in projects
            for tag in project.get("tags", [])
        }
    )

    # -----------------------------------------------------------------------
    # Render helper
    # -----------------------------------------------------------------------

    def render(template_name, out_path, **ctx):

        template = env.get_template(template_name)

        html = template.render(
            site=site,
            **ctx,
        )

        out_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        out_path.write_text(
            html,
            encoding="utf-8",
        )

        print(
            f"  wrote {out_path.relative_to(ROOT)}"
        )

    # -----------------------------------------------------------------------
    # HOME
    # -----------------------------------------------------------------------

    render(
        "home.html.j2",
        DIST / "index.html",
        profile=profile,
        projects=projects,
        research_items=research_items,
        active_nav="Home",
    )

    # -----------------------------------------------------------------------
    # WORK INDEX
    # -----------------------------------------------------------------------

    render(
        "work_index.html.j2",
        DIST / "work" / "index.html",
        projects=projects,
        all_tags=all_tags,
        active_nav="Work",
    )

    # -----------------------------------------------------------------------
    # INDIVIDUAL PROJECT PAGES
    # -----------------------------------------------------------------------

    for project in projects:

        render(
            "project.html.j2",
            DIST / "work" / f"{project['slug']}.html",
            p=project,
            active_nav="Work",
        )

    # -----------------------------------------------------------------------
    # RESEARCH INDEX
    # -----------------------------------------------------------------------

    if research_items:

        render(
            "research_index.html.j2",
            DIST / "research" / "index.html",
            research_items=research_items,
            active_nav="Research",
        )

        # ---------------------------------------------------------------
        # INDIVIDUAL RESEARCH PAGES
        # ---------------------------------------------------------------

        for research in research_items:

            render(
                "research.html.j2",
                DIST
                / "research"
                / research["slug"]
                / "index.html",
                research=research,
                active_nav="Research",
            )

    # -----------------------------------------------------------------------
    # ABOUT
    # -----------------------------------------------------------------------

    render(
        "about.html.j2",
        DIST / "about.html",
        profile=profile,
        active_nav="About",
    )

    # -----------------------------------------------------------------------
    # CV
    # -----------------------------------------------------------------------

    render(
        "cv.html.j2",
        DIST / "cv.html",
        cv=cv,
        active_nav="CV",
    )

    # -----------------------------------------------------------------------
    # BUILD SUMMARY
    # -----------------------------------------------------------------------

    print("\n----------------------------------------")
    print("Build complete.")
    print("----------------------------------------")
    print(f"Projects : {len(projects)}")
    print(f"Research : {len(research_items)}")
    print(f"Output   : {DIST}")
    print("----------------------------------------\n")


if __name__ == "__main__":
    main()