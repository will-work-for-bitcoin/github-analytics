#!/usr/bin/env python3
"""
github-analytics.py — GitHub repository analytics CLI

Fetch repository stats, contributor info, commit history, and more.
Pure Python 3.7+, zero dependencies.

Usage:
    python github-analytics.py <owner>/<repo>
    python github-analytics.py <owner>/<repo> --contributors
    python github-analytics.py <owner>/<repo> --recent
    python github-analytics.py <owner>/<repo> --json

Support: https://github.com/yourusername/github-analytics
"""

import sys
import json
import urllib.request
from datetime import datetime


def fetch_github(url):
    """Fetch from GitHub API"""
    req = urllib.request.Request(url, headers={
        "User-Agent": "github-analytics/1.0",
        "Accept": "application/vnd.github.v3+json"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def get_repo_stats(owner, repo):
    """Get repository statistics"""
    base = f"https://api.github.com/repos/{owner}/{repo}"
    
    data = fetch_github(base)
    if "error" in data:
        return data
    
    # Get contributors count
    contrib_data = fetch_github(f"{base}/contributors?per_page=1")
    total_contributors = contrib_data.get("Link", "").split("page=")[1].split(">;")[0] if "page=" in contrib_data.get("Link", "") else "N/A"
    
    return {
        "name": data.get("full_name", "N/A"),
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "watchers": data.get("watchers_count", 0),
        "open_issues": data.get("open_issues_count", 0),
        "language": data.get("language", "N/A"),
        "size": f"{data.get('size', 0) / 1024:.1f} MB",
        "created": data.get("created_at", "N/A")[:10],
        "updated": data.get("updated_at", "N/A")[:10],
        "license": data.get("license", {}).get("spdx_id", "N/A"),
        "contributors": total_contributors,
        "description": data.get("description", "N/A")[:100],
    }


def display_stats(stats):
    """Display repository stats"""
    if "error" in stats:
        print(f"❌ Error: {stats['error']}\n")
        return
    
    print(f"\n  ╔══════════════════════════════════════════════════════════════╗")
    print("  ║            📊 GITHUB REPOSITORY ANALYTICS                ║")
    print("  ╚══════════════════════════════════════════════════════════════╝")
    print(f"  Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"  ┌── REPOSITORY INFO ─────────────────────────────────────────┐")
    print(f"  │ Name:       {stats['name']}")
    print(f"  │ Language:   {stats['language']}")
    print(f"  │ License:    {stats['license']}")
    print(f"  │ Size:       {stats['size']}")
    print(f"  │ Created:    {stats['created']}")
    print(f"  │ Updated:    {stats['updated']}")
    print("  └─────────────────────────────────────────────────────────────┘\n")
    
    print(f"  ┌── STATISTICS ────────────────────────────────────────────┐")
    print(f"  │ ⭐ Stars:      {stats['stars']:>10,}")
    print(f"  │ 🍴 Forks:      {stats['forks']:>10,}")
    print(f"  │ 👀 Watchers:   {stats['watchers']:>10,}")
    print(f"  │ 🐛 Issues:     {stats['open_issues']:>10,}")
    print(f"  │ 👥 Contributors: {stats['contributors']:>10}")
    print("  └─────────────────────────────────────────────────────────────┘\n")
    
    if stats.get('description'):
        print(f"  Description: {stats['description']}")
    
    print(f"  📦 Source: https://github.com/yourusername/github-analytics\n")


def display_json(stats):
    """Output stats as JSON"""
    print(json.dumps(stats, indent=2))


def main():
    args = sys.argv[1:]
    
    if not args or "--help" in args or "-h" in args:
        print(__doc__)
        return
    
    repo_path = args[0]
    flags = [a for a in args[1:] if a.startswith("--")]
    
    if "/" not in repo_path:
        print("❌ Usage: python github-analytics.py <owner>/<repo>\n")
        return
    
    owner, repo = repo_path.split("/", 1)
    stats = get_repo_stats(owner, repo)
    
    if "json" in flags:
        display_json(stats)
    elif "contributors" in flags:
        contrib_url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
        contribs = fetch_github(contrib_url)
        if "error" not in contribs:
            print(f"\n  Contributors to {owner}/{repo}:\n")
            for i, c in enumerate(contribs[:20], 1):
                print(f"  {i:>3}. {c['login']:<30} {c['contributions']:>4} contributions")
            print()
        else:
            print(f"❌ Error: {contribs['error']}\n")
    elif "recent" in flags:
        commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=10"
        commits = fetch_github(commits_url)
        if "error" not in commits:
            print(f"\n  Recent commits to {owner}/{repo}:\n")
            for c in commits:
                commit = c['commit']
                msg = commit['message'].split('\n')[0][:60]
                date = commit['committer']['date'][:10]
                author = commit['author']['name'] if commit['author'] else 'N/A'
                print(f"  • {date}  {author:<20}  {msg}")
            print()
        else:
            print(f"❌ Error: {commits['error']}\n")
    else:
        display_stats(stats)


if __name__ == "__main__":
    main()
