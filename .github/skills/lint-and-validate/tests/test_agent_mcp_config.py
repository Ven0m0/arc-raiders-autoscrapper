import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def read_frontmatter(path: Path) -> str:
    """Return the YAML frontmatter block from an agent file."""
    match = re.match(r"^---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.DOTALL)
    assert match is not None, f"missing frontmatter in {path}"
    return match.group(1)


def read_model(path: Path) -> str:
    """Return the configured primary model for an agent."""
    match = re.search(
        r'^model:\s*["\']?([^\n"\']+)["\']?$', read_frontmatter(path), re.MULTILINE
    )
    assert match is not None, f"missing model in {path}"
    return match.group(1)


def test_workspace_mcp_config_includes_selected_servers():
    """Workspace MCP config should expose the newly selected high-value servers."""
    mcp_config = json.loads(
        (REPO_ROOT / ".vscode" / "mcp.json").read_text(encoding="utf-8")
    )
    servers = mcp_config["mcpServers"]

    assert servers["eslint"]["args"] == ["-y", "@eslint/mcp@latest"]
    assert servers["chrome-devtools"]["args"] == [
        "-y",
        "chrome-devtools-mcp@latest",
        "--headless",
        "--no-usage-statistics",
    ]
    assert servers["next-devtools"]["args"] == ["-y", "next-devtools-mcp@latest"]
    assert servers["vercel"]["url"] == "https://mcp.vercel.com"
    assert servers["netlify"]["args"] == ["-y", "@netlify/mcp"]
    assert servers["reddit"]["args"] == [
        "--from",
        "git+https://github.com/adhikasp/mcp-reddit.git",
        "mcp-reddit",
    ]
    assert servers["ast-grep"]["args"] == ["-y", "@notprolands/ast-grep-mcp@latest"]


def test_code_agents_keep_only_specialized_structural_mcp_servers():
    """Coding-focused agents should keep only the specialized MCP servers they still need."""
    expected_servers = {
        "agents/coder.agent.md": (
            "eslint:",
            "ast-grep:",
            "repomix:",
            "semgrep:",
            "sequential-thinking:",
        ),
        "agents/reviewer.agent.md": (
            "eslint:",
            "ast-grep:",
            "repomix:",
            "semgrep:",
            "sequential-thinking:",
        ),
        "agents/codebase-maintainer.agent.md": (
            "eslint:",
            "ast-grep:",
            "repomix:",
            "sequential-thinking:",
        ),
        "agents/explorer.agent.md": ("ast-grep:", "repomix:"),
    }

    for relative_path, server_names in expected_servers.items():
        frontmatter = read_frontmatter(REPO_ROOT / relative_path)
        for server_name in server_names:
            assert server_name in frontmatter


def test_agents_include_specialized_mcp_servers_in_frontmatter():
    """Agents should expose the specialized MCP servers they need in frontmatter."""
    expected_servers = {
        "agents/researcher.agent.md": ("reddit:",),
        "agents/frontend-specialist.agent.md": (
            "chrome-devtools:",
            "vercel:",
            "netlify:",
        ),
        "agents/debug.agent.md": (
            "chrome-devtools:",
            "semgrep:",
            "sequential-thinking:",
        ),
        "agents/workflow-engineer.agent.md": ("vercel:", "netlify:"),
        "agents/repo-architect.agent.md": ("vercel:", "netlify:"),
    }

    for relative_path, server_names in expected_servers.items():
        frontmatter = read_frontmatter(REPO_ROOT / relative_path)
        for server_name in server_names:
            assert server_name in frontmatter


def test_all_agents_use_supported_primary_models():
    """Agents should use the repo-standard primary models only."""
    supported_models = {"GPT-5.4", "claude-sonnet-4.6"}
    expected_models = {
        "agents/orchestrator.agent.md": "claude-sonnet-4.6",
        "agents/explorer.agent.md": "GPT-5.4",
        "agents/planner.agent.md": "GPT-5.4",
        "agents/researcher.agent.md": "GPT-5.4",
        "agents/coder.agent.md": "claude-sonnet-4.6",
        "agents/reviewer.agent.md": "GPT-5.4",
        "agents/debug.agent.md": "claude-sonnet-4.6",
        "agents/workflow-engineer.agent.md": "claude-sonnet-4.6",
        "agents/frontend-specialist.agent.md": "claude-sonnet-4.6",
        "agents/git.agent.md": "claude-sonnet-4.6",
        "agents/codebase-maintainer.agent.md": "claude-sonnet-4.6",
        "agents/doc-writer.agent.md": "GPT-5.4",
        "agents/repo-architect.agent.md": "GPT-5.4",
        "agents/arch-linux-expert.agent.md": "claude-sonnet-4.6",
        "agents/janitor.agent.md": "claude-sonnet-4.6",
    }

    for path in (REPO_ROOT / "agents").glob("*.agent.md"):
        model = read_model(path)
        assert model in supported_models, f"unsupported model {model!r} in {path}"

    for relative_path, expected_model in expected_models.items():
        path = REPO_ROOT / relative_path
        model = read_model(path)
        assert model == expected_model


def test_primary_agents_drop_deprecated_mcp_servers():
    """Optimized agents should avoid deprecated or now-default MCP server choices."""
    deprecated_servers = (
        "context7:",
        "serena:",
        "gitmcp:",
        "grep-app:",
        "fetch:",
        "memory:",
        "morph-mcp:",
        "github-mcp-server:",
        "fast-filesystem:",
        "octocode:",
        "exa:",
        "ref-tools:",
        "next-devtools:",
        "playwright:",
    )

    for path in (REPO_ROOT / "agents").glob("*.agent.md"):
        frontmatter = read_frontmatter(path)
        for server_name in deprecated_servers:
            assert server_name not in frontmatter, f"unexpected {server_name} in {path}"
