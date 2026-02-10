#!/usr/bin/env python3
"""Static site generator for Bushy Pony. Zero external dependencies."""

import json
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(ROOT, "build")
PAGES = os.path.join(ROOT, "pages")
STATIC = os.path.join(ROOT, "static")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def build_nav(nav_items, current_page):
    lines = []
    for item in nav_items:
        if "url" in item:
            lines.append(
                f'                <li><a href="{item["url"]}" target="_blank">{item["title"]}</a></li>'
            )
        else:
            page = item["page"]
            href = "index.html" if page == nav_items[0]["page"] else f"{page}.html"
            if page == current_page:
                lines.append(
                    f'                <li><strong><a href="{href}">{item["title"]}</a></strong></li>'
                )
            else:
                lines.append(
                    f'                <li><a href="{href}">{item["title"]}</a></li>'
                )
    return "\n".join(lines)


def main():
    nav_items = json.loads(read(os.path.join(ROOT, "nav.json")))
    layout = read(os.path.join(ROOT, "layout.html"))

    # Clean build directory
    if os.path.exists(BUILD):
        shutil.rmtree(BUILD)
    os.makedirs(BUILD)

    first_page = None

    for item in nav_items:
        if "page" not in item:
            continue

        page = item["page"]
        if first_page is None:
            first_page = page

        content = read(os.path.join(PAGES, f"{page}.html"))
        nav_html = build_nav(nav_items, page)
        title = f"Bushy Pony — {item['title']}"

        html = layout.replace("{{nav}}", nav_html)
        html = html.replace("{{content}}", content)
        html = html.replace("{{title}}", title)

        write(os.path.join(BUILD, f"{page}.html"), html)

        # First page is also index.html
        if page == first_page:
            write(os.path.join(BUILD, "index.html"), html)

    # Copy static assets
    if os.path.isdir(STATIC):
        for entry in os.listdir(STATIC):
            src = os.path.join(STATIC, entry)
            dst = os.path.join(BUILD, entry)
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

    # Copy CNAME if it exists
    cname = os.path.join(ROOT, "CNAME")
    if os.path.isfile(cname):
        shutil.copy2(cname, os.path.join(BUILD, "CNAME"))

    print(f"Built {len(os.listdir(BUILD))} files in build/")


if __name__ == "__main__":
    main()
