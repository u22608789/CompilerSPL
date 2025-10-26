import re

LABEL_DEF_RE = re.compile(r'^\s*REM\s+([A-Za-z]+\d+)\s*$')
JUMP_RE = re.compile(r'\b(GOTO|THEN)\s+([A-Za-z]+\d+)\b')

def intermediate_to_basic(lines: list[str], start: int = 10, step: int = 10) -> list[str]:
    """Turn unnumbered intermediate code into numbered BASIC with label resolution."""
    # 1) Number the lines (skip blanks)
    numbered = []
    lnum = start
    for raw in lines:
        if raw.strip() == "":
            continue
        numbered.append((lnum, raw))
        lnum += step

    # 2) Build label → lineNumber map (strict label-only REM lines)
    label_line = {}
    for ln, text in numbered:
        m = LABEL_DEF_RE.match(text)
        if m:
            label_line[m.group(1)] = ln  # e.g., "DO1" -> 70

    # 3) Rewrite GOTO/THEN label usages
    out = []
    for ln, text in numbered:
        def repl(m):
            cmd, lab = m.group(1), m.group(2)
            target = label_line.get(lab)
            # If label not found, keep as-is
            return f"{cmd} {target if target is not None else lab}"

        new_text = JUMP_RE.sub(repl, text)
        out.append(f"{ln} {new_text}")
    return out
