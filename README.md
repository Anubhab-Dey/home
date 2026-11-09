# anubhabdey.in

**Live site:** https://anubhabdey.in/  
**Source:** https://github.com/Anubhab-Dey/home  
**Owner:** Anubhab Dey (`Anubhab-Dey`, personal GitHub account)

A lightweight, static personal website with an engineering portfolio, a public-safe résumé and a separate **Scriptures** reading library. Caddy serves the site on a Debian VPS behind Cloudflare. It is **not hosted by GitHub Pages**; pushing commits does not automatically deploy changes to the live VPS.

## Site and scripture source layout

- `index.html`, `assets/`: the portfolio, résumé section and public-safe assets.
- `scriptures/index.html`, `scriptures/library.css`, `scriptures/catalog.js`: the live V5 library layout and interactive catalogue. The three older books appear first; the ten V5 additions are on the expanded shelf.
- `scriptures/facsimile/*.html`: five historical scan reading pages (HTML templates only).
- `scriptures/reader.js`: shared reading controls.
- `scripts/build_scriptures.py`: generates three V3 English full-text readers and their source TXT files.
- `scripts/build_v5_texts.py` + `scripts/v5_manifest.json`: five additional V5 historical editions and expected source metadata.
- `scripts/add_editorial_note.py`: idempotently adds the independent-library disclaimer to every HTML reader, facsimile page, and the library homepage.
- `docs/SCRIPTURES_V4.md`, `docs/SOURCES_V5.md`, `LICENSES.md`: provenance, historical limitations, and reuse information.

**Only source code and static templates are versioned.** The complete Project Gutenberg TXT/HTML reader files and Wikimedia Commons PDF scans are generated/downloaded during a verified build, and must not be committed. This is an independently managed Caddy website, **not GitHub Pages**. `git push` does not publish to your VPS.

## Build locally before website deployment

Python 3 and a trusted HTTPS client are needed on the build machine; the VPS runs only Caddy and serves static assets. The two standard-library Python builders accept an offline source directory, avoiding the Python SSL trust issue on some Windows installations:

```powershell
# Run at repository root; source files are obtained over verified HTTPS first.
py -3 scripts/build_scriptures.py --offline-source-dir 'C:\temporary\trusted-gutenberg'
py -3 scripts/build_v5_texts.py --offline-source-dir 'C:\temporary\trusted-gutenberg'
py -3 scripts/add_editorial_note.py .
```

For those offline builds, the directory must contain eight **fully downloaded, authenticated historical source texts** named `pg2388.txt`, `pg3283.txt`, `pg66208.txt`, `pg2526.txt`, `pg21918.txt`, `pg61937.txt`, `pg34125.txt`, and `pg16295.txt`. Both builders validate identifiers, provenance, and end-of-file licence notices before writing public outputs. The disclaimer patcher is idempotent; rerun it **after** the reader builders so generated HTML pages also contain the notice. Do not disable HTTPS certificate verification.

The six historical scanned PDFs (the 1922 bilingual Gītā plus five V5 facsimiles) must be retrieved from the specific public-domain source records, with verified HTTPS, source metadata, PDF signature, size and available hashes checked against the source manifest. **This repository does not provide a single integrated full-release builder yet; use the tested V4/V5 deployment workflow or develop an equivalent preflighted one before a new VPS release.** Never deploy source-only Git files directly over the live website: it would omit required book downloads.

The editorial disclaimer clarifies that library inclusion is for reading/preservation/study, not agreement with every text or translator. Original Sanskrit, editorial interpretation, historical medical/legal/astrological literature and verified modern guidance are different categories.

## Deployment boundary and safety

Live document root: `/var/www/anubhabdey.in`. Deployment must first assemble **all** generated HTML, source TXT, and scan PDFs in an isolated local staging directory. Check that the complete public tree exists, preserve all unrelated live site files, and apply changed pages through same-filesystem staging and reversible switch. Verify the live Caddy origin over HTTPS before removing successful temporary archives and rollback copies. Preserve recovery materials on failed rollback. No new root-level Caddy/DNS change is necessary.

Never copy `.git`, `scripts/`, `.env`, keys, manifests with private metadata, or build inputs into Caddy's public root. Source files tracked here do not include GitHub credentials. Use the **personal** `Anubhab-Dey/home` repository only; the work GitHub account is outside this project's scope.

## Public résumé and privacy

The public PDF in `assets/` omits personal email, telephone number and residential address. It includes professional history and education. The complete private résumé is **not** part of this repository. If you update the source résumé, regenerate and privacy-check the public edition before committing it.

## Licensing

See `LICENSES.md`. The website's original code, creative content and résumé are not offered under a general open-source licence by default. The historical texts have separate provenance and redistribution terms; their source notices are preserved when built. GitHub visibility does not itself grant an unrestricted licence.
