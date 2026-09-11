#!/usr/bin/env python3
"""Validate AsciiDoc cross-references in docs/.

Asciidoctor does not fail, or even warn, on an xref whose target does not
exist -- it silently emits a dead anchor. This script catches those before
they reach the published site.

The id rules below mirror the asciidoctor invocation in
enonic/release-tools/generate-docs (action.yml), which passes `-a idprefix=`
and leaves `idseparator` at its default. If that invocation changes, update
ID_PREFIX / ID_SEPARATOR to match.

Usage: python3 .github/scripts/check-xrefs.py [docs-dir]
"""

import os
import re
import sys

ID_PREFIX = ''
ID_SEPARATOR = '_'

# <<target>> or <<target,label>>. Targets never span lines in this corpus.
XREF_RE = re.compile(r'<<([^,>\s][^,>]*?)(?:,[^>]*)?>>')
HEADING_RE = re.compile(r'^(={1,6})\s+(.+?)\s*$', re.M)
ATTR_ANCHOR_RE = re.compile(r'^\[#([A-Za-z_:][\w:.-]*)\]\s*$', re.M)
BLOCK_ANCHOR_RE = re.compile(r'^\[\[([A-Za-z_:][\w:.-]*)(?:,[^\]]*)?\]\]\s*$', re.M)
INLINE_ANCHOR_RE = re.compile(r'\[\[([A-Za-z_:][\w:.-]*)(?:,[^\]]*)?\]\]')
# Source blocks are literal; xrefs inside them are not parsed.
FENCE_RE = re.compile(r'^(-{4,}|\.{4,}|\+{4,}|={4,}|\*{4,}|_{4,})\s*$')


def auto_id(title):
    """Reproduce Asciidoctor's generated section id for a title."""
    t = title.strip()
    t = re.sub(r'<<([^,>]*?)(?:,([^>]*))?>>', lambda m: m.group(2) or m.group(1), t)
    t = re.sub(r'\{[^}]*\}', '', t)          # attribute references
    t = re.sub(r'[`*_^~#+]', '', t)          # inline formatting marks
    t = t.lower()
    t = re.sub(r'[^a-z0-9 _.-]', '', t)      # drop everything else
    t = re.sub(r'\s+', ID_SEPARATOR, t.strip())
    return ID_PREFIX + t


def collect(path, text):
    ids = set(ATTR_ANCHOR_RE.findall(text))
    ids |= set(BLOCK_ANCHOR_RE.findall(text))
    ids |= set(INLINE_ANCHOR_RE.findall(text))
    auto = {auto_id(m.group(2)) for m in HEADING_RE.finditer(text)}
    return {'explicit': ids, 'auto': auto}


def source_lines(text):
    """Yield (lineno, line) for lines outside literal/source blocks."""
    fence = None
    for n, line in enumerate(text.split('\n'), 1):
        m = FENCE_RE.match(line)
        if m:
            token = m.group(1)[0]
            if fence is None:
                fence = token
                continue
            if fence == token:
                fence = None
            continue
        if fence is None:
            yield n, line


def main():
    docs = sys.argv[1] if len(sys.argv) > 1 else 'docs'
    if not os.path.isdir(docs):
        print(f'error: no such directory: {docs}', file=sys.stderr)
        return 2

    files = {}
    for root, _, names in os.walk(docs):
        for n in sorted(names):
            if n.endswith('.adoc'):
                p = os.path.join(root, n)
                with open(p, encoding='utf-8') as fh:
                    files[p] = fh.read()

    index = {p: collect(p, s) for p, s in files.items()}
    problems = []

    for path, text in sorted(files.items()):
        for lineno, line in source_lines(text):
            for m in XREF_RE.finditer(line):
                target = m.group(1).strip()
                if target.startswith(('http:', 'https:', 'mailto:')):
                    continue

                if '#' in target:
                    rel, _, anchor = target.partition('#')
                    if rel == '':
                        tpath = path
                    else:
                        # Relative to the referencing file, else to the docs root.
                        cand = os.path.normpath(
                            os.path.join(os.path.dirname(path), rel)) + '.adoc'
                        if cand not in files:
                            alt = os.path.normpath(os.path.join(docs, rel)) + '.adoc'
                            cand = alt if alt in files else cand
                        tpath = cand
                    if tpath not in files:
                        problems.append((path, lineno, target,
                                         'target file not found'))
                        continue
                    if anchor == '':
                        continue  # whole-page link
                    known = index[tpath]
                    if anchor in known['explicit'] or anchor in known['auto']:
                        continue
                    # Cross-file/# targets are emitted verbatim: no title matching.
                    hint = ''
                    if auto_id(anchor) in known['auto']:
                        hint = f" -- did you mean '{auto_id(anchor)}'?"
                    elif anchor.replace('-', ID_SEPARATOR) in known['auto']:
                        alt = anchor.replace('-', ID_SEPARATOR)
                        hint = f" -- did you mean '{alt}'?"
                    problems.append((path, lineno, target,
                                     'anchor does not exist' + hint))
                else:
                    known = index[path]
                    # Bare targets also resolve by section title (natural xref).
                    if (target in known['explicit'] or target in known['auto']
                            or auto_id(target) in known['auto']):
                        continue
                    elsewhere = [
                        os.path.relpath(os.path.splitext(other)[0],
                                        os.path.dirname(path))
                        for other, oi in sorted(index.items())
                        if other != path
                        and (target in oi['explicit'] or target in oi['auto'])
                    ]
                    hint = ''
                    if elsewhere:
                        opts = ' or '.join(f"'{r}#{target}'" for r in elsewhere)
                        hint = f' -- defined in another file, use {opts}'
                    problems.append((path, lineno, target,
                                     'no such anchor or section in this file' + hint))

    annotate = os.environ.get('GITHUB_ACTIONS') == 'true'
    for path, lineno, target, why in problems:
        print(f'{path}:{lineno}: <<{target}>> {why}')
        if annotate:
            msg = f'<<{target}>> {why}'.replace('%', '%25').replace(
                '\r', '%0D').replace('\n', '%0A')
            print(f'::error file={path},line={lineno},title='
                  f'Broken cross-reference::{msg}')

    n = len(problems)
    print(f'\nchecked {len(files)} files: '
          f'{n if n else "no"} broken cross-reference{"" if n == 1 else "s"}')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
