#!/usr/bin/env python3
"""Add an editorial-independence notice to anubhabdey.in Scriptures HTML.

Stdlib-only; works on a V4 or V5 HTML snapshot, idempotent, and does not
modify original scripture TXT/PDF files. Optionally generates preflight hashes.
"""
import argparse
import hashlib
from pathlib import Path

MARKER = 'scripture-editorial-note'
LONG = '''<aside class="scripture-editorial-note" id="library-editorial-note" aria-labelledby="library-editorial-heading">
  <h2 id="library-editorial-heading">About this library · Included for study, not endorsement</h2>
  <p>This collection is provided for reading, preservation and study. Including a scripture, translation, commentary or historical edition does <strong>not</strong> mean that I personally agree with or endorse every passage, interpretation, claim or prescribed practice it contains. Original texts, translators' interpretations and editorial notes are distinct, and different editions or traditions may differ. Please consult each work's attribution and edition-specific warnings.</p>
  <p>Historical discussions of medicine, law and astrology are presented as source literature, not as modern medical or legal advice or verified scientific conclusions.</p>
</aside>'''
SHORT = '''<aside class="scripture-editorial-note scripture-editorial-note--compact" aria-label="About this library">
 <strong>Included for study, not endorsement.</strong> This edition is part of a reference library; its inclusion does not imply my personal agreement with every passage, assertion or interpretation. <a href="/scriptures/#library-editorial-note">Read the library's editorial note</a>.
</aside>'''
CSS = '''
/* Editorial independence: same unobtrusive note across the library and readers. */
.scripture-editorial-note{margin:30px 0 34px;padding:20px 24px;border:1px solid var(--line,#4d5c52);border-left:3px solid var(--accent,#ba9b62);border-radius:6px;background:var(--bg-soft,#1b2523);color:var(--text,#f0eee8);font:inherit;line-height:1.7}
.scripture-editorial-note h2{font-size:clamp(17px,2vw,21px);line-height:1.4;letter-spacing:-.015em;margin:0 0 9px;color:var(--text,#f0eee8)}
.scripture-editorial-note p{font-size:13px;line-height:1.8;margin:0;color:var(--muted,var(--text,#f0eee8))}
.scripture-editorial-note p+p{margin-top:9px}
.scripture-editorial-note--compact{font-size:13px;margin:20px 0 26px;padding:15px 18px;color:var(--muted,var(--text,#f0eee8))}
.scripture-editorial-note a{color:var(--accent,#ba9b62);text-decoration:underline;text-underline-offset:3px}
@media(max-width:590px){.scripture-editorial-note{padding:15px 16px;margin:23px 0 28px}}
'''

def replace_once(source: str, needle: str, notice: str, relative: str) -> str:
    matches = source.count(needle)
    if matches < 1:
        raise ValueError(f'{relative}: required insertion marker absent: {needle}')
    return source.replace(needle, notice + '\n' + needle, 1)

def apply(root: Path, manifest: bool) -> None:
    landing = root / 'scriptures/index.html'
    css_file = root / 'scriptures/library.css'
    if not landing.is_file() or not css_file.is_file():
        raise ValueError('Expected scriptures/index.html and scriptures/library.css in snapshot')
    pages = [landing]
    for folder in ('read', 'facsimile'):
        pages += sorted((root / 'scriptures' / folder).glob('*.html'))
    if len(pages) < 4:
        raise ValueError(f'Expected at least 3 reader pages, found only {len(pages) - 1}')
    files = pages + [css_file]
    updates: list[tuple[Path,str,str,bytes]] = []
    for f in files:
        rel = f.relative_to(root).as_posix()
        raw_original = f.read_bytes()
        old = raw_original.decode('utf-8')
        if f == css_file:
            if '/* Editorial independence:' in old:
                new = old
            else:
                new = old.rstrip() + '\n' + CSS
        elif MARKER in old:
            # Already patched; safe to repeat with no duplicates.
            if 'Included for study, not endorsement' not in old:
                raise ValueError(f'{rel}: marker exists but notice not found; needs manual review')
            new = old
        elif f == landing:
            if '<section class="lib-featured"' not in old:
                raise ValueError(f'{rel}: unfamiliar library template; no changes made')
            new = replace_once(old, '<section class="lib-featured"', LONG, rel)
        elif '/read/' in rel:
            new = replace_once(old, '<div class="reader-controls"', SHORT, rel)
        elif '/facsimile/' in rel:
            new = replace_once(old, '<div class="facsimile-actions"', SHORT, rel)
        else:
            raise ValueError(f'Unhandled file: {rel}')
        updates.append((f, old, new, raw_original))

    # Validate all changes before writing anything.
    for f, old, new, _ in updates:
        if f == css_file:
            if '.scripture-editorial-note' not in new:
                raise ValueError('CSS notice style missing')
        else:
            if new.count('<aside class="scripture-editorial-note') != 1:
                raise ValueError(f'{f}: expected one notice, not {new.count(MARKER)}')
            if new.count('</aside>') < 1:
                raise ValueError(f'{f}: notice closing element missing')
            if not new.startswith('<!doctype html>'):
                raise ValueError(f'{f}: HTML doctype changed unexpectedly')
    if manifest:
        manifest_file = root / '__original.sha256'
        if manifest_file.exists():
            raise ValueError('Preflight manifest already exists')
        # Write bytes explicitly: Path.write_text() translates LF to CRLF on
        # Windows, leaving a trailing carriage return in Bash manifest paths.
        manifest_file.write_bytes(''.join(
            f'{hashlib.sha256(raw).hexdigest()}  {f.relative_to(root).as_posix()}\n'
            for f, _, _, raw in updates
        ).encode('ascii'))
    for f, old, new, _ in updates:
        if old != new:
            f.write_text(new, encoding='utf-8', newline='')
    print(f'Editorial note present in {len(pages)} HTML pages; updated styles; source TXT/PDF untouched.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('site_dir', type=Path)
    parser.add_argument('--preflight-manifest', action='store_true')
    ns = parser.parse_args()
    apply(ns.site_dir, ns.preflight_manifest)
