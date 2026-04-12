# Claude Code Best Practices

Save tokens, reduce costs, and get better results from Claude Code.

Based on official Anthropic documentation, community benchmarks, and real-world testing. These practices can reduce your Claude Code usage by 50-70%.

## Three Ways to Use This

### Option A: Read the Guide

Open [`claude-code-best-practices.html`](claude-code-best-practices.html) in your browser for a visual, non-technical guide. Save as PDF with Cmd+P / Ctrl+P.

Or view it online: [coach-foundation.github.io/claude-code-best-practices](https://coach-foundation.github.io/claude-code-best-practices/claude-code-best-practices.html)

### Option B: Smart Optimizer (recommended)

Analyzes your existing setup, shows what's recommended vs what you have, and merges best practices without overwriting your customizations.

```bash
git clone https://github.com/Coach-Foundation/claude-code-best-practices.git
cd claude-code-best-practices/smart-optimizer
claude
```

Claude will automatically analyze your config and walk you through the recommendations.

### Option C: One-Command Setup

Replaces your config with optimized defaults (backs up your existing files first).

```bash
git clone https://github.com/Coach-Foundation/claude-code-best-practices.git
cd claude-code-best-practices
python3 claude-setup.py    # Mac/Linux
python claude-setup.py     # Windows
```

Then use `cc` instead of `claude` to start.

## What Gets Configured

| Setting | What it does | Impact |
|---------|-------------|--------|
| MAX_THINKING_TOKENS=10000 | Caps expensive thinking tokens | ~70% thinking cost reduction |
| Subagent model: Haiku | Uses cheaper model for helper tasks | ~80% cheaper subagents |
| Effort level: medium | Reduces output verbosity | 50-70% fewer output tokens |
| Auto-compact: 75% | Triggers compaction earlier | More buffer, fewer emergencies |
| Context Efficiency rules | Stops Claude from echoing, narrating, re-reading | Major output reduction |
| .claudeignore | Blocks scanning of junk files | Prevents context blowups |

## Recommended Plugins

After setup, start a Claude Code session and install these:

```
/install-plugin superpowers      # Structured workflows (planning, TDD, code review)
/install-plugin context7          # Always-current library documentation
/install-plugin code-simplifier   # Code quality reviews
```

## Contributing

Found a tip that saves tokens? Open a PR or issue.

## License

MIT
