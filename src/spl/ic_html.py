# src/spl/ic_html.py
import html, re

LABEL_RE = re.compile(r'^\s*REM\s+([A-Za-z]+\d+)\s*$')
GOTO_RE  = re.compile(r'\bGOTO\s+([A-Za-z]+\d+)\b')
THEN_RE  = re.compile(r'\bTHEN\s+([A-Za-z]+\d+)\b')

def _link_labels(line: str) -> str:
    # THEN Lx / GOTO Lx → THEN <a href="#Lx">Lx</a>
    def repl_goto(m): return f'GOTO <a href="#{m.group(1)}">{m.group(1)}</a>'
    def repl_then(m): return f'THEN <a href="#{m.group(1)}">{m.group(1)}</a>'
    line = GOTO_RE.sub(repl_goto, line)
    line = THEN_RE.sub(repl_then, line)
    return line

def write_intermediate_html(lines: list[str], out_path: str) -> None:
    """
    Render the un-numbered intermediate code as a linked HTML page:
    - REM Lx lines become anchors (#Lx)
    - GOTO Lx / THEN Lx become links to those anchors
    """
    items = []
    for raw in lines:
        text = html.escape(raw)
        # make links for THEN/GOTO labels
        linked = _link_labels(text)

        # make REM Lx an anchor target
        m = LABEL_RE.match(raw)
        if m:
            label = m.group(1)
            linked = f'<a id="{label}"></a>{linked}'

        items.append(f'<li><code>{linked}</code></li>')

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Intermediate Code</title>
<style>
  body {{ font: 14px/1.4 system-ui, sans-serif; margin: 24px; }}
  ol {{ padding-left: 2em; }}
  code {{ white-space: pre; }}
  .hint {{ color:#666; margin-bottom:8px; }}
</style>
</head>
<body>
  <h1>Intermediate Code</h1>
  <p class="hint">Labels appear as <code>REM Lx</code>; jumps link to those labels.</p>
  <ol>
    {''.join(items)}
  </ol>
</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_doc)
