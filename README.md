# Claude Code Best Practices

Save tokens, reduce costs, and get better results from Claude Code.

Based on official Anthropic documentation, community benchmarks, and real-world testing. These practices can reduce your Claude Code usage by 50-70%.

## Get Started

### Interactive Setup Wizard (recommended)

Step-by-step guide designed for non-technical users. Takes about 10 minutes.

Open [`index.html`](index.html) in your browser or view online: [coach-foundation.github.io/claude-code-best-practices](https://coach-foundation.github.io/claude-code-best-practices/)

The wizard walks you through:
1. Choosing between fresh install or smart optimizer
2. Running the setup command
3. Verifying it works
4. Installing recommended plugins
5. Learning essential commands
6. Saving money with best practices

### Quick Option A: Fresh Install

New to Claude Code or want optimized defaults? One-command setup (backs up your existing files):

```bash
git clone https://github.com/Coach-Foundation/claude-code-best-practices.git
cd claude-code-best-practices
python3 claude-setup.py    # Mac/Linux
python claude-setup.py     # Windows
```

Then use `cc` instead of `claude` to start.

### Quick Option B: Smart Optimizer

Have existing settings you want to keep? Claude analyzes your setup and merges best practices without overwriting customizations:

```bash
git clone https://github.com/Coach-Foundation/claude-code-best-practices.git
cd claude-code-best-practices/smart-optimizer
claude
```

Claude will automatically walk you through the recommendations.

### Option C: Read the Full Guide

Open [`claude-code-best-practices.html`](claude-code-best-practices.html) in your browser for a visual, non-technical guide. Save as PDF with Cmd+P / Ctrl+P.

Or view it online: [coach-foundation.github.io/claude-code-best-practices/claude-code-best-practices.html](https://coach-foundation.github.io/claude-code-best-practices/claude-code-best-practices.html)

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
