#!/usr/bin/env python3
"""Fetch three verified historical editions and build static self-hosted reader pages.

Only run after reviewing sources and rights; retains exact upstream text with notices.
No third-party Python packages. No arbitrary URLs/paths. Fails before writing on
missing, truncated, or unexpected source data. May be run repeatedly safely.
"""
from pathlib import Path
import argparse
import html
import os
import tempfile
from urllib.request import Request, urlopen

BOOKS = (
    (2388, 'gita-arnold', 'Bhagavad Gita · The Song Celestial', 'Sir Edwin Arnold', 'The Song Celestial'),
    (3283, 'upanishads-paramananda', 'The Upanishads', 'Swami Paramananda', 'The Upanishads'),
    (66208, 'vishnu-purana-dutt', 'Vishnu Purana', 'Manmatha Nath Dutt', 'Vishnupuranam'),
)

BASE = Path(__file__).resolve().parent.parent

def fetch(book_id):
    url = f'https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt'
    req = Request(url, headers={'User-Agent': 'AnubhabDeY-Scriptures-Library/1.0 (personal archive)'})
    with urlopen(req, timeout=50) as response:
        if response.status != 200:
            raise RuntimeError(f'{book_id}: HTTP {response.status}')
        payload = response.read(8_000_001)
    if not (30_000 < len(payload) < 8_000_000):
        raise ValueError(f'{book_id}: unexpected length {len(payload)}')
    return payload.decode('utf-8-sig')

def validate(book_id, text, expected):
    head = text[:6000].casefold()
    if f'ebook #{book_id}' not in head and f'ebook # {book_id}' not in head:
        raise ValueError(f'{book_id}: expected ebook marker missing')
    if 'project gutenberg' not in head or expected.casefold() not in head:
        raise ValueError(f'{book_id}: unexpected title or missing provenance')
    if 'END OF THE PROJECT GUTENBERG EBOOK' not in text[-35000:]:
        raise ValueError(f'{book_id}: book may be truncated')
    if 'FULL PROJECT GUTENBERG LICENSE' not in text[-45000:].upper():
        raise ValueError(f'{book_id}: licence missing')

def reader(title, translator, slug, text):
    t=html.escape(title)
    tr=html.escape(translator)
    body=html.escape(text)
    return f"""<!doctype html><html lang="en" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="dark light"><title>{t} | Scriptures | Anubhab Dey</title><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/styles.css"><link rel="stylesheet" href="/scriptures/library.css"><script>try{{let t=localStorage.getItem('ad-theme');if(t==='light'||t==='dark')document.documentElement.dataset.theme=t}}catch(e){{}}</script><script src="/assets/site.js" defer></script><script src="/scriptures/reader.js" defer></script></head><body><a class="skip-link" href="#main">Skip to text</a><main class="reader-shell" id="main"><a class="reader-back" href="/scriptures/">← ALL SCRIPTURES</a><header class="reader-header"><h1>{t}</h1><p>Historical English edition by {tr}. Readable here, downloadable as the complete original source text.</p></header><div class="reader-controls"><button type="button" data-reader-step="-1" aria-label="Decrease reading text size">A−</button><span id="reader-font-value" aria-live="polite">19 px</span><button type="button" data-reader-step="1" aria-label="Increase reading text size">A+</button><a href="/scriptures/books/{slug}.txt" download>Download complete TXT ↓</a></div><p class="reader-note">This is a historical English translation (and, where identified, commentary), not the Sanskrit original. The complete downloaded text includes its provenance and licence notices. Use browser Find to locate passages.</p><pre class="reader-body" data-book-text>{body}</pre><div class="reader-controls"><a href="/scriptures/">← Back to library</a></div></main></body></html>"""

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--offline-source-dir',type=Path,help='Use previously downloaded pgID.txt files for fully offline repeatable builds')
    args=p.parse_args()
    results=[]
    for book_id,slug,title,translator,expected in BOOKS:
        if args.offline_source_dir:
            text=(args.offline_source_dir / f'pg{book_id}.txt').read_text(encoding='utf-8-sig')
        else:
            text=fetch(book_id)
        validate(book_id,text,expected)
        results.append((slug, text, reader(title,translator,slug,text)))
        print(f'Validated {book_id}: {len(text):,} chars')
    # All inputs validated before any outputs are changed.
    for slug,text,content in results:
        for rel,data in ((f'scriptures/books/{slug}.txt',text),(f'scriptures/read/{slug}.html',content)):
            path=BASE / rel
            path.parent.mkdir(parents=True,exist_ok=True)
            fd,tmp=tempfile.mkstemp(prefix=f'.{path.name}.',dir=path.parent)
            try:
                with os.fdopen(fd,'w',encoding='utf-8',newline='') as fp:fp.write(data)
                os.chmod(tmp,0o644)
                os.replace(tmp,path)
            finally:
                if os.path.exists(tmp):os.unlink(tmp)
            print(f'Generated {rel}')

if __name__=='__main__': main()
