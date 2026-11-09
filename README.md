# anubhabdey.in

**Live site:** https://anubhabdey.in/  
**Source:** https://github.com/Anubhab-Dey/home  
**Owner:** Anubhab Dey (`Anubhab-Dey`, personal GitHub account)

A lightweight, static personal website with an engineering portfolio, a public-safe résumé and a separate **Scriptures** reading library. Caddy serves the site on a Debian VPS behind Cloudflare. It is **not hosted by GitHub Pages**; pushing commits does not automatically deploy changes to the live VPS.

## Structure

- `index.html`: homepage (including résumé, project cards, and links).
- `assets/`: CSS, small JavaScript, favicon, social card, and public-safe résumé PDF.
- `scriptures/index.html`, `scriptures/library.css`, `scriptures/reader.js`: catalog and reader assets.
- `scripts/build_scriptures.py`: standard-library-only builder for historical editions.
- `LICENSES.md`: sources and redistribution considerations.

No Node tooling, framework, database, tracking scripts or web application server is required.

## Build and preview the Scriptures library

The repo holds **source code, not generated book files**. To serve books from your domain, build them before deploying. The builder downloads and validates complete text editions from Project Gutenberg, then creates self-contained HTML readers and the original TXT downloads. These files are intentionally ignored by Git.

```powershell
# Run in this repository directory, with Python 3 available.
py -3 scripts/build_scriptures.py
```

On Windows systems where Python's HTTPS CA chain is not configured, retrieve the three official Gutenberg source text files through a trusted HTTPS client into a temporary directory as `pg2388.txt`, `pg3283.txt`, `pg66208.txt`. Then run:

```powershell
py -3 scripts/build_scriptures.py --offline-source-dir 'C:\path\to\trusted-downloads'
```

The offline builder still checks the edition identifiers, provenance markers, title, expected ending and full licence section. **Never disable TLS certificate verification.** Generated outputs:

- `scriptures/read/{gita-arnold,upanishads-paramananda,vishnu-purana-dutt}.html`
- `scriptures/books/{gita-arnold,upanishads-paramananda,vishnu-purana-dutt}.txt`

Preview with `py -3 -m http.server 8000` and visit `http://localhost:8000/`. For rights and translation provenance, see `LICENSES.md`; the English editions are historical, not the original Sanskrit or authoritative sampradaya commentaries.

## Deployment

The live root is `/var/www/anubhabdey.in`; Caddy's existing configuration serves that directory. Build the complete Scriptures library in a temporary local workspace, package **only public web files**, and transfer them via SSH to a temporary VPS staging directory. Validate the staged content; switch it into place with a rollback plan and delete successful staging/transfer artifacts. The site's original one-shot deployer is maintained separately from this repository and can be adapted to work with a source ZIP from this repository.

To create a deployment archive manually after a successful build:

```powershell
# In repository root, using Windows PowerShell 7 (tar installed)
tar -czf "$env:TEMP\anubhabdey-site-deploy.tar.gz" --exclude=.git --exclude=.github --exclude=scripts --exclude=README.md --exclude=LICENSES.md --exclude=.gitignore -C . .
```

The output archive must contain `index.html`, `assets/`, `scriptures/index.html`, `scriptures/read/*.html` and `scriptures/books/*.txt` before deployment. Upload to VPS staging, then verify the homepage, reader pages, and downloads. **Do not copy this repository wholesale into the public web root** because that would expose development/configuration files. After successful release, remove temporary archives and staging directories.

Cloudflare DNS, SSL and Caddy are configured independently. This repository does not contain VPS secrets, SSH keys or Cloudflare credentials. Do not add them.

## Public résumé and privacy

The public PDF in `assets/` omits personal email, telephone number and residential address. It includes professional history and education. The complete private résumé is **not** part of this repository. If you update the source résumé, regenerate and privacy-check the public edition before committing it.

## Licensing

See `LICENSES.md`. The website's original code, creative content and résumé are not offered under a general open-source licence by default. The historical texts have separate provenance and redistribution terms; their source notices are preserved when built. GitHub visibility does not itself grant an unrestricted licence.
