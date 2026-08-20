#!/usr/bin/env python3
"""
Site builder for sanjay-bhandari.com.np

Usage:
    python3 build.py

To add a project:
    1. Create content/projects/<slug>.json following the shape of an existing entry.
    2. Re-run this script.

To remove a project:
    1. Delete content/projects/<slug>.json.
    2. Re-run this script.

No other file needs to change. The build regenerates dist/ from scratch every run.
"""
import json
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
DIST = ROOT / "dist"

TIER_ORDER = {"S": 0, "A": 1, "B": 2, "micro": 3}


def load(name):
    with open(CONTENT / name, encoding="utf-8") as f:
        return json.load(f)


def load_projects():
    projects = []
    for path in sorted((CONTENT / "projects").glob("*.json")):
        with open(path, encoding="utf-8") as f:
            projects.append(json.load(f))
    projects.sort(key=lambda p: (TIER_ORDER.get(p.get("tier", "B"), 9), p["title"]))
    return projects


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    (DIST / "work").mkdir()

    shutil.copytree(STATIC, DIST / "static")

    # Temporary direct route for the multi-hop baseline paper.
# PDF lives directly inside static/ for now.

    multi_hop_pdf = STATIC / "multi-hop-baseline-model.pdf"

    if multi_hop_pdf.exists():
        paper_route = DIST / "multi-hop-baseline-model"
        shutil.copy2(multi_hop_pdf, paper_route)
    
        print("  ✓ /multi-hop-baseline-model → multi-hop-baseline-model.pdf")
    else:
        print("  ! Multi-hop PDF not found:")
        print(f"    {multi_hop_pdf}")

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    site = load("site.json")
    profile = load("profile.json")
    cv = load("cv.json")
    projects = load_projects()
    all_tags = sorted({t for p in projects for t in p.get("tags", [])})

    def render(template_name, out_path, **ctx):
        tpl = env.get_template(template_name)
        html = tpl.render(site=site, **ctx)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
        print(f"  wrote {out_path.relative_to(ROOT)}")

    render("home.html.j2", DIST / "index.html",
           profile=profile, projects=projects, active_nav="Home")

    render("work_index.html.j2", DIST / "work" / "index.html",
           projects=projects, all_tags=all_tags, active_nav="Work")

    for p in projects:
        render("project.html.j2", DIST / "work" / f"{p['slug']}.html",
               p=p, active_nav="Work")

    render("about.html.j2", DIST / "about.html",
           profile=profile, active_nav="About")

    render("cv.html.j2", DIST / "cv.html",
           cv=cv, active_nav="CV")

    print(f"\nBuild complete \u2014 {len(projects)} project page(s). Output in {DIST}")


if __name__ == "__main__":
    main()
