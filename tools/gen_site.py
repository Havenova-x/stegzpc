"""Generates the whole /site folder (pages, sitemap.xml, search index, robots, 404).
Run automatically by BUILD.bat; safe to run any time:  python tools/gen_site.py
latest.json and announcement.json are NEVER overwritten if they exist."""
import datetime
import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import version as V  # noqa: E402

SITE = os.path.join(ROOT, "site")
BASE = V.SITE_URL
TODAY = datetime.date.today().isoformat()
E = html.escape

# slug, group, title, h1, description, keywords, intro, [bullets], (faq q, faq a)
PAGES = [
 ("stegz", "Product", "StegZ - hide, protect & compress files | Free Windows app", "StegZ: one small app for hiding, protecting and compressing files",
  "StegZ is a free Windows app that hides files inside normal images, packs them into .stegz archives, adds AES-256 passwords and can self-destruct.",
  "stegz, stegsz, steg, stes, stegz app, stegz download, stegz windows",
  "StegZ puts three everyday jobs in one clean window: tuck files inside an ordinary picture, squeeze them into a compact .stegz archive, or lock them behind a password.",
  ["Browse your whole PC like a file manager, then right-click to hide or protect", "Works offline - your files never leave your PC", "Updates itself quietly in the background"],
  ("What is StegZ?", "A free Windows utility for privacy and organisation: hide files in images, create .stegz archives, password-protect and optionally self-destruct them.")),
 ("steg", "Product", "Steg - the simple steg tool for Windows | StegZ", "Steg made simple: a no-fuss steg tool",
  "Looking for a steg tool? StegZ hides files inside JPG, PNG and BMP images with drag and drop. Free for Windows.",
  "steg, steg tool, steg app, steg windows, simple steg, steg software",
  "'Steg' is short for steganography: keeping the existence of data low-key by tucking it inside something ordinary. StegZ gives you that with drag and drop instead of terminal commands.",
  ["Drop an image, drop your files, press Create", "The picture still opens like any other photo", "Optional password and self-destruct"],
  ("Is steg the same as encryption?", "No. Steg conceals that something is there; encryption scrambles it. StegZ lets you combine both with an optional AES-256 password.")),
 ("stegs", "Product", "Stegs - hide and archive files with StegZ", "Stegs and archives, handled",
  "Stegs, stegz or stegsz - StegZ is the one app that hides files in images and builds compact .stegz archives.",
  "stegs, stegs tool, stegs app, stegs download, stegz stegs",
  "If you searched for 'stegs', you want a quick way to make and open steg files. StegZ creates them in two clicks and reads them back just as fast.",
  ["Hide in an image or save a standalone archive", "Scan any image to see if it contains StegZ data", "Integrity check warns you about damaged files"],
  ("Can StegZ open stegs made on another PC?", "Yes - any StegZ build can open files made by another StegZ, as long as you have the password if one was set.")),
 ("stegsz", "Product", "StegSZ / StegZ - download the Windows app", "StegSZ, Stegz, Steg - you found it",
  "Searching for stegsz, stes or stegz? This is the official StegZ site: download the free Windows app that hides and compresses files.",
  "stegsz, stes, stegz, steg z, stegz official, stegsz download",
  "The name is easy to mistype - stegsz, stes, steg-z - but the app is one thing: StegZ. This is its official home, with the real installer straight from GitHub Releases.",
  ["Official download, checksum shown on the download page", "Free, no account, no ads", "Windows 10 and 11"],
  ("How is StegZ spelled?", "S-t-e-g-Z. People also type stegsz, stes or steg z - they all lead here.")),
 ("archive-tool", "Tools", "Free archive tool for Windows | StegZ", "A modern archive tool that also hides and locks files",
  "StegZ is a free archive tool: make .zip and .stegz archives, add AES-256 passwords, hide archives inside images.",
  "archive tool, archive maker, file archiver, free archiver windows, archive software, stegz archive",
  "Most archivers stop at zip. StegZ also creates its own .stegz archives that carry a checksum, optional password and optional self-destruct rules.",
  ["Create .stegz or standard .zip", "Checksum verified before every extraction", "Drag and drop everywhere"],
  ("Does it replace my zip tool?", "It covers everyday zipping and unzipping, plus extras zip tools do not have.")),
 ("compress-tools", "Tools", "Compress tools - zip, unzip, .stegz | StegZ", "Compress tools in one place",
  "Compress files to .zip or .stegz, unzip and decompress, rename and create files - the StegZ File Tools tab.",
  "compress tools, compress files, file compression tool, compress folder, compression app windows",
  "The File Tools tab gathers the small jobs: compress to .stegz, make a normal .zip, unzip, decompress, create a blank file, rename.",
  ["Compress folders as well as files", "Background processing keeps the window responsive", "Progress bar on every task"],
  ("Which compress format should I choose?", "Use .zip to share with anyone. Use .stegz when you want a checksum, a password or self-destruct.")),
 ("file-compressor", "Tools", "File compressor for Windows | StegZ", "A file compressor that stays out of your way",
  "Shrink and bundle files with StegZ: deflate compression, folders supported, progress shown, no installs beyond the app.",
  "file compressor, compress file size, shrink files, bundle files, compressor windows",
  "Bundle a pile of files into a single compact archive. StegZ uses reliable deflate compression and shows progress so you know it is working.",
  ["Handles whole folders", "Never touches the originals", "Safe unzip: blocks unsafe paths inside archives"],
  ("Does compression lose quality?", "No. The compression is lossless - what you extract is identical to what you packed.")),
 ("zip-and-unzip-tool", "Tools", "Zip and unzip tool | StegZ", "Zip and unzip without the clutter",
  "Zip files and unzip archives with StegZ File Tools. Standard .zip output opens on every computer.",
  "zip tool, unzip tool, zip files windows, unzip files, zip maker, free zip",
  "Need a plain .zip for a friend or a form upload? Pick files or a folder, choose where to save, done.",
  ["Standard zip - opens everywhere", "Unzip protects against malicious paths", "One tab, no menus to hunt through"],
  ("Can StegZ unzip password zips?", "StegZ's unzip is for normal zips. Password protection is available when you create .stegz archives or hide files in images.")),
 ("open-rar-zip-7z-files", "Tools", "Open RAR, ZIP, 7Z and TAR files | StegZ", "Open RAR, ZIP, 7Z and TAR files",
  "StegZ opens and extracts ZIP, RAR, 7Z, TAR, GZ, ISO and more, with a WinRAR-style right-click menu: Extract here and Extract to folder.",
  "open rar, open 7z, rar extractor, 7z extractor, zip extractor, winrar alternative, extract here, archive viewer windows",
  "StegZ doubles as an archive viewer. Double-click a ZIP, RAR, 7Z, TAR, GZ, ISO or CAB file, pick what you want and extract - or right-click and choose Extract here.",
  ["Right-click: Extract here, Extract to folder, Quick zip", "Select many files and they are handled together", "Listed in Open with and Windows Default apps"],
  ("Can StegZ open RAR files?", "Yes, using the free 7-Zip if installed, or Windows' built-in tar for simple archives. ZIP, TAR and 7Z need nothing extra.")),
 ("stegz-file-format", "Guides", "The .stegz file format explained | StegZ", "The .stegz file format",
  "What is a .stegz file? A compact archive with a checksum, optional AES-256 password and optional self-destruct rules.",
  "stegz file, .stegz, stegz format, stegz extension, what is a stegz file",
  "A .stegz file starts with a small header (magic, version, flags), then a SHA-256 checksum and the locked archive data. Because of the header and an obfuscation layer, generic zip tools cannot read it - StegZ can.",
  ["Header carries flags for password and self-destruct", "SHA-256 checksum detects damage or tampering", "The obfuscation layer is a format lock, not encryption - passwords provide the real security"],
  ("Is .stegz secure?", "The format lock stops casual tools. For real confidentiality, set the AES-256 password.")),
 ("open-stegz-file", "Guides", "How to open a .stegz file | StegZ", "How to open a .stegz file",
  "Open a .stegz file by double-clicking it once StegZ is installed, or drop it onto the Extract tab.",
  "open stegz file, open .stegz, stegz opener, extract stegz, stegz viewer, unstegz",
  "Install StegZ and tick 'Associate .stegz files' during setup: double-click opens the Extract tab ready to go. Otherwise drag the file onto the app.",
  ["Enter the password if one was set", "Choose an output folder or accept the default", "Self-destruct archives warn you before they are used up"],
  ("It says wrong password or damaged - why?", "StegZ cannot tell those apart safely. Re-check the password; if it is right, the file was probably altered or cut off in transit.")),
 ("hide-files-in-image", "Guides", "Hide files in an image - step by step | StegZ", "How to hide files inside an image",
  "Hide any files inside a JPG, PNG or BMP picture with StegZ. The picture still opens normally.",
  "hide files in image, hide files in picture, hide file in photo, hide files inside jpg, image file hider",
  "Open the Hide tab, drop a carrier image, add the files you want to tuck inside, optionally set a password, then press Create. Your original image is never overwritten.",
  ["Supports JPG, PNG and BMP carriers", "Folders can be hidden too", "A new image is saved alongside the original"],
  ("Will social media keep the hidden data?", "Usually not - most platforms re-compress uploads, which removes it. Share the file directly (cloud drive, email attachment) instead.")),
 ("image-steganography-tool", "Guides", "Image steganography tool | StegZ", "Image steganography, minus the maths",
  "A friendly image steganography tool: StegZ appends your data after the image end marker so pictures look and behave normally.",
  "image steganography, steganography tool, steganography software, steganography app, steg image",
  "Classic steganography hides bits inside pixels. StegZ takes the practical route: data follows the image's end marker, which viewers ignore, so quality is untouched and capacity is large.",
  ["No quality loss in the picture", "Large capacity compared to pixel tricks", "Honest about limits: not meant to defeat forensic analysis"],
  ("Is this military-grade steganography?", "No marketing claims here. StegZ is for privacy and tidiness, and pairs steganography with real AES-256 passwords when you need protection.")),
 ("hide-zip-in-jpg", "Guides", "Hide a zip in a JPG | StegZ", "Hide a zip inside a JPG - the easy way",
  "Instead of copy /b command lines, use StegZ to hide a zip-like archive inside a JPG with a password.",
  "hide zip in jpg, hide zip in image, zip inside jpg, copy /b image zip, jpg zip hider",
  "The old trick joins a zip to a JPG with a command line. StegZ does the same idea with checks, a password option and a one-click scan to find it again.",
  ["No command line", "Integrity checked on extraction", "Remove the payload any time by re-hiding"],
  ("Can 7-Zip open it?", "StegZ adds a format lock, so generic archive tools will not read the payload. Use StegZ.")),
 ("extract-hidden-files-from-image", "Guides", "Extract hidden files from an image | StegZ", "Extract hidden files from an image",
  "Got an image with StegZ data inside? Drop it on the Extract tab to pull the files out.",
  "extract hidden files from image, find hidden files in picture, reveal hidden files, image extractor",
  "Use Scan first to see what is inside without changing anything, then Extract to save the files into a folder of your choice.",
  ["Scan lists file names and sizes", "Extraction path-checked for safety", "Recent files list for quick access"],
  ("How do I know an image has hidden data?", "Run it through the Scan tab. It reports whether StegZ data is present and its size.")),
 ("check-image-for-hidden-data", "Guides", "Check an image for hidden data | StegZ", "Check any image for hidden StegZ data",
  "The Scan tab tells you whether an image or .stegz file contains hidden data, its size, password and self-destruct status.",
  "check image hidden data, scan image hidden files, detect hidden files in image, image scanner",
  "Scanning is read-only: StegZ never alters the file and never counts a scan as an extraction.",
  ["See size, password and expiry settings", "List files when you provide the password", "Integrity shown as verified or failed"],
  ("Does scanning use up a burn-after-reading limit?", "No. Only a successful extraction counts.")),
 ("password-protect-files", "Guides", "Password protect files on Windows | StegZ", "Password protect files and folders",
  "Add an AES-256 password to hidden files and .stegz archives with StegZ - no cloud, no account.",
  "password protect files, password protect folder, lock files windows, encrypt files with password",
  "Type a password on the Hide tab and the archive inside is encrypted. Without the password nobody - including us - can open it.",
  ["Password never stored", "Works for images and .stegz", "Show/hide toggle prevents typos"],
  ("I forgot the password. Can you recover it?", "No. There is no backdoor by design.")),
 ("aes-256-file-encryption", "Guides", "AES-256 file encryption | StegZ", "AES-256 encryption for your files",
  "StegZ uses standard AES-256 zip encryption for password-protected content.",
  "aes 256 encryption, aes file encryption, encrypt files aes, strong file encryption windows",
  "Password-protected StegZ archives use AES-256 zip encryption through a well-known open library, layered under StegZ's own format.",
  ["Industry-standard cipher", "Wrong password rejected cleanly", "Choose a long passphrase for best results"],
  ("Is AES-256 unbreakable?", "It is considered very strong; the weak point is usually the password, so use a long one.")),
 ("self-destructing-files", "Guides", "Self-destructing files | StegZ", "Self-destructing files that really wipe",
  "Create archives that expire on a date or after a set number of opens, then overwrite their own contents.",
  "self destructing files, self destruct file, expiring files, file expiry, auto delete file",
  "Opt in per archive and combine rules: a date, a limit on opens (viewing can count too), or a timer that starts when someone first opens it. When a rule is met StegZ overwrites the hidden payload with zeros.",
  ["Date, open limit and timer after first open", "You must confirm at creation - it is irreversible", "Only the archive you created is affected; copying it first keeps an untouched copy"],
  ("Can it delete other files on my PC?", "Never. It only wipes the payload inside the exact file you made.")),
 ("burn-after-reading-files", "Guides", "Burn after reading files | StegZ", "Burn-after-reading for files",
  "Set max opens to 1 and the archive destroys itself after the first successful extraction.",
  "burn after reading, read once file, one time file, destroy after opening, privnote for files",
  "Think of Privnote, but for files and fully offline. Set Max opens to 1 on the Hide tab and share the result.",
  ["First successful open wins", "Wrong passwords do not use it up", "Works inside images or as .stegz"],
  ("What if I open it by mistake?", "That counts. Confirm carefully when creating one.")),
 ("file-hider-for-windows", "Tools", "File hider for Windows | StegZ", "A file hider for Windows that looks like a photo",
  "Hide private files in a photo with StegZ, a free Windows file hider with passwords and self-destruct.",
  "file hider, file hider windows, hide files windows, hide private files, hide folder windows",
  "No hidden-attribute games that anyone can reveal in Explorer. Your files ride inside a normal-looking image.",
  ["Pick any carrier photo", "Add a password for real protection", "Recent files and scan for quick recovery"],
  ("Is this for hiding illegal content?", "No - you are responsible for what you store. See the Terms page.")),
 ("secure-file-archive", "Tools", "Secure file archive maker | StegZ", "Make a secure file archive",
  "Create a secure archive with checksum, AES-256 password and optional self-destruct using StegZ.",
  "secure archive, secure file archive, protected archive, encrypted archive maker, secure zip",
  "A secure archive should tell you if it was damaged. StegZ stores a SHA-256 checksum and checks it before extracting.",
  ["Checksum + optional password", "Optional expiry and open limits", "No account or internet required"],
  ("Where is the checksum stored?", "In the archive header, and verified before any file is written out.")),
 ("steganography-tool-windows", "Tools", "Steganography tool for Windows 10 & 11 | StegZ", "Steganography for Windows 10 and 11",
  "Install StegZ with a normal Windows installer: Start Menu entry, optional right-click menu, uninstall in Apps & Features.",
  "steganography windows, steganography windows 11, steganography download, steganography exe",
  "StegZ installs like any other Windows program, with optional right-click entries on images ('Hide in StegZ', 'Extract with StegZ').",
  ["Standard installer and uninstaller", "Choose your install folder", "Silent auto-updates"],
  ("Does it need admin rights?", "The installer asks once for permission to install in Program Files. The app itself runs normally.")),
 ("privacy-tools", "Tools", "Privacy tools for everyday files | StegZ", "Everyday privacy tools",
  "StegZ is a small privacy toolkit: hide, lock, expire and compress files locally.",
  "privacy tools, privacy software, file privacy, offline privacy tool, private files app",
  "Local, offline, no telemetry. The only network use is checking for updates and downloading the installer from GitHub.",
  ["No account", "No analytics", "Plain-language privacy policy"],
  ("What does StegZ send over the internet?", "Only update checks: two small public JSON files, then the installer if one is available. Nothing about you or your files.")),
 ("rename-and-create-files", "Tools", "Create and rename files | StegZ", "Create and rename files in two clicks",
  "StegZ File Tools can create blank files and rename existing ones safely.",
  "create new file, rename file tool, blank file creator, make empty file windows",
  "Sometimes you just need an empty file or a quick rename. StegZ refuses names Windows disallows and will not overwrite existing files.",
  ["Blank file anywhere", "Safe rename with checks", "Part of the free File Tools tab"],
  ("Will rename overwrite a file with the same name?", "No, it stops and tells you.")),
 ("free-file-utilities", "Tools", "Free file utilities | StegZ", "Free file utilities in one window",
  "Zip, unzip, compress, hide, protect, rename and create files with StegZ, free.",
  "free file utilities, file tools windows, file utility app, file management tools",
  "One light app instead of five. Dark and light themes, drag and drop, background processing.",
  ["Free", "Small download", "Auto-updating"],
  ("Is StegZ really free?", "Yes. No ads, no accounts.")),
 ("how-it-works", "Guides", "How StegZ works | StegZ", "How StegZ works",
  "A plain-English look at how StegZ hides, locks and verifies your files.",
  "how stegz works, how steganography works, stegz explained, stegz payload format",
  "Files are packed into a zip, optionally AES-encrypted, scrambled with a format lock, given a SHA-256 checksum and appended after the image's end marker.",
  ["Pack and encrypt", "Lock and checksum", "Append and verify"],
  ("Does the picture change?", "The visible picture is identical. The file is just larger.")),
]

STATIC = [  # plain pages built separately
 ("download", "Download", "Download StegZ for Windows - free", "Download StegZ", "Download the free StegZ Windows installer straight from GitHub Releases, with checksum and progress.", "download stegz, stegz download, stegz installer, stegz exe, stegz setup"),
 ("tools", "Hub", "StegZ tools - archive, compress, hide, protect", "All tools", "Every StegZ tool and use case in one list.", "stegz tools, compress tools, archive tools, file tools"),
 ("guides", "Hub", "StegZ guides and how-tos", "All guides", "How to hide files in images, open .stegz files, password protect and more.", "stegz guides, how to hide files, how to open stegz"),
 ("faq", "Hub", "StegZ FAQ", "Frequently asked questions", "Answers about StegZ, steg, .stegz files, passwords, self-destruct and updates.", "stegz faq, steg faq"),
 ("changelog", "Hub", "StegZ changelog and latest version", "Latest version and changelog", "What is new in the latest StegZ release.", "stegz changelog, stegz latest version, stegz update"),
 ("privacy", "Legal", "StegZ Privacy Policy", "Privacy Policy", "StegZ privacy policy.", "stegz privacy"),
 ("terms", "Legal", "StegZ License and Terms", "License & Terms", "StegZ end-user license and disclaimer.", "stegz terms, stegz license"),
 ("sitemap", "Hub", "StegZ site map", "Site map", "Every page on the StegZ website.", "stegz sitemap"),
]


def read_md(name):
    with open(os.path.join(ROOT, "docs", name), encoding="utf-8") as f:
        txt = f.read()
    out, in_list = [], False
    for ln in txt.splitlines():
        if ln.startswith("# "):
            continue
        s = ln.strip()
        if s[:2] in ("- ",) or (s[:1].isdigit() and s[1:3] in (". ",)):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{E(s.split(' ', 1)[1])}</li>")
            continue
        if in_list and not s.startswith(" "):
            out.append("</ul>")
            in_list = False
        if s and not (in_list and ln.startswith("   ")):
            out.append(f"<p>{E(s)}</p>")
        elif s and in_list:
            out[-1] = out[-1][:-5] + " " + E(s) + "</li>"
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def faq_ld(q, a):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}]}


APP_LD = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "StegZ",
          "operatingSystem": "Windows 10, Windows 11", "applicationCategory": "UtilitiesApplication",
          "url": BASE + "/", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
          "description": "Hide files inside images, compress to .stegz, password-protect and self-destruct."}

ALL = [(p[0], p[2], p[4], p[5], p[1]) for p in PAGES] + [(s[0], s[2], s[4], s[5], s[1]) for s in STATIC]


def head(title, desc, kw, slug, ld=None):
    url = f"{BASE}/" if slug == "index" else f"{BASE}/{slug}.html"
    ld_tags = "".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in (ld or []))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="keywords" content="{E(kw)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#05080f">
<meta property="og:type" content="website"><meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/style.css">
{ld_tags}
</head>
<body data-release-base="{V.RELEASE_BASE}" data-installer="{V.INSTALLER_NAME}" data-fallback="https://github.com/{V.GITHUB_USER}/{V.GITHUB_REPO}/releases/latest/download/{V.INSTALLER_NAME}">
"""


def header():
    return """<div id="ann" class="ann" hidden></div>
<header class="top"><div class="wrap bar">
<a class="brand" href="index.html" aria-label="StegZ home">Steg<b>Z</b></a>
<nav aria-label="Main"><a href="tools.html">Tools</a><a href="guides.html">Guides</a><a href="faq.html">FAQ</a><a href="changelog.html">Changelog</a></nav>
<div class="search"><input id="q" type="search" placeholder="Search StegZ  ( / )" autocomplete="off" aria-label="Search the site"><ul id="results" hidden></ul></div>
<a class="btn sm" href="download.html?auto=1">Download</a>
</div></header>
<main>
"""


def footer():
    cols = {}
    for slug, title, _d, _k, g in ALL:
        cols.setdefault(g, []).append((slug, title.split(" | ")[0].split(" - ")[0]))
    order = [("Tools", "Tools"), ("Guides", "Guides"), ("Product", "Product"), ("Download", "Get"), ("Hub", "Site"), ("Legal", "Legal")]
    out = '</main>\n<footer><div class="wrap"><div class="fgrid">'
    for key, label in order:
        items = cols.get(key, [])
        if key == "Hub":
            items = [i for i in items if i[0] in ("faq", "changelog", "sitemap", "tools", "guides")]
        out += f'<div><h4>{label}</h4>' + "".join(f'<a href="{s}.html">{E(t)}</a>' for s, t in items) + "</div>"
    out += f'</div><p class="tiny">&copy; {datetime.date.today().year} StegZ &middot; Free Windows file utility &middot; <span data-ver></span></p></div></footer>\n<script src="assets/app.js" defer></script>\n</body></html>\n'
    return out


def dl_widget():
    return """<section id="get" class="card dl" data-dl>
<h2>Download StegZ</h2>
<p class="muted">Windows 10 / 11 &middot; version <span data-ver>latest</span> &middot; <span data-size></span></p>
<a class="btn big" id="dl-btn" href="__FALLBACK__" role="button">Download for Windows</a>
<div class="pbar" id="dl-bar" hidden><i></i></div>
<p id="dl-status" class="muted" aria-live="polite"></p>
<p class="tiny">SHA-256 <code data-sha>shown after load</code> &middot; <a id="dl-direct" href="__FALLBACK__">direct link</a></p>
<div class="androidbox"><a class="btn big alt" id="an-btn" href="#" role="button" hidden>Download for Android (APK)</a>
<p id="an-soon" class="muted">Android version: <b>coming soon&hellip;</b></p>
<p class="tiny" id="an-meta" hidden>Android <span data-av></span> &middot; <span data-asize></span> &middot; SHA-256 <code data-asha></code><br>Open the file on your phone; allow &ldquo;install from this source&rdquo; if Android asks.</p></div>
</section>""".replace("__FALLBACK__", f"https://github.com/{V.GITHUB_USER}/{V.GITHUB_REPO}/releases/latest/download/{V.INSTALLER_NAME}")


def related(slug, group):
    same = [p for p in PAGES if p[0] != slug and p[1] == group]
    other = [p for p in PAGES if p[0] != slug and p[1] != group]
    pick = (same + other)[:6]
    return '<h2>Related</h2><div class="chips">' + "".join(f'<a href="{p[0]}.html">{E(p[3])}</a>' for p in pick) + "</div>"


def write(slug, content):
    with open(os.path.join(SITE, f"{slug}.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def build_page(p):
    slug, group, title, h1, desc, kw, intro, bullets, (fq, fa) = p
    body = f"""<section class="wrap page"><p class="eyebrow">{E(group)}</p><h1>{E(h1)}</h1><p class="lead">{E(intro)}</p>
<div class="grid3">{''.join(f'<div class="card"><p>{E(b)}</p></div>' for b in bullets)}</div>
<div class="cta"><a class="btn big" href="download.html?auto=1">Download StegZ - free</a><a class="btn ghost" href="index.html#features">See features</a></div>
<h2>{E(fq)}</h2><p>{E(fa)}</p>
{related(slug, group)}</section>"""
    write(slug, head(title, desc, kw, slug, [faq_ld(fq, fa), APP_LD]) + header() + body + footer())


def build_index():
    feats = [("Hide in images", "Tuck files inside a normal JPG, PNG or BMP. The picture still opens like any other.", "hide-files-in-image"),
             ("Password lock", "One toggle for AES-256 encryption. No account, no cloud.", "password-protect-files"),
             ("Self-destruct", "Date, open limit or a timer after first open - then truly wiped.", "self-destructing-files"),
             ("Compress", "Make .zip or compact .stegz archives, unzip, decompress.", "compress-tools"),
             ("Integrity check", "SHA-256 verified before every extraction.", "secure-file-archive"),
             ("Auto-updates", "Quiet background updates with a tiny install banner.", "changelog")]
    cards = "".join(f'<a class="card link" href="{s}.html"><h3>{E(t)}</h3><p>{E(d)}</p></a>' for t, d, s in feats)
    faqs = [("Is StegZ free?", "Yes. No ads, accounts or tracking."), ("Does it work offline?", "Yes. Only update checks use the internet."),
            ("What is a .stegz file?", "StegZ's own compact archive with a checksum, optional password and optional self-destruct."),
            ("Why do I also see 'steg', 'stegs', 'stegsz'?", "They are common spellings people search for - they all lead to StegZ.")]
    fq = "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faqs)
    allfaq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    links = "".join(f'<a href="{p[0]}.html">{E(p[3])}</a>' for p in PAGES)
    body = f"""<section class="hero"><div class="wrap two">
<div><p class="eyebrow">Free for Windows</p><h1>Hide. Protect. <span class="grad">Compress.</span></h1>
<p class="lead">StegZ hides files inside ordinary images, packs them into compact .stegz archives, locks them with AES-256 and can destroy them on schedule. Plain to use, quiet to run.</p>
<div class="cta"><a class="btn big" href="download.html?auto=1">Download for Windows</a><a class="btn ghost" href="how-it-works.html">How it works</a></div>
<p class="tiny">Version <span data-ver>latest</span> &middot; Offline &middot; No account</p></div>
<div class="card mock" aria-hidden="true"><div class="scan"></div>
<p class="mono">holiday.jpg <em>looks normal</em></p><p class="mono">&#x2514; 3 files inside &middot; 18.4 MB</p><p class="mono">&#x2514; AES-256 &middot; checksum OK</p><p class="mono">&#x2514; burns after 1 open</p></div>
</div></section>
<section id="features" class="wrap"><h2>Everything in one small window</h2><div class="grid3">{cards}</div></section>
<section class="wrap"><h2>Three steps</h2><ol class="steps"><li><b>Drop</b> an image and your files</li><li><b>Choose</b> a password or self-destruct (optional)</li><li><b>Create</b> - share the result, open it any time with StegZ</li></ol></section>
<section class="wrap">{dl_widget()}</section>
<section class="wrap"><h2>Questions</h2>{fq}</section>
<section class="wrap"><h2>Explore</h2><div class="chips">{links}</div></section>"""
    write("index", head("StegZ - hide files in images, compress & protect | Free Windows app",
                        "StegZ is a free Windows app: hide files inside images, create .stegz archives, AES-256 passwords, self-destruct, zip tools. Also searched as steg, stegs, stegsz.",
                        "stegz, steg, stegs, stegsz, stes, archive, compress tools, hide files in image, steganography windows", "index", [APP_LD, allfaq])
          + header() + body + footer())


def build_static():
    for slug, group, title, h1, desc, kw in STATIC:
        extra = ""
        if slug == "download":
            extra = dl_widget() + '<p class="muted">The download starts inside this page straight from GitHub Releases - no GitHub page opens. If your browser blocks that, it falls back to a normal direct download automatically. After installing, StegZ updates itself.</p>'
        elif slug == "tools":
            extra = '<div class="grid3">' + "".join(f'<a class="card link" href="{p[0]}.html"><h3>{E(p[3])}</h3><p>{E(p[4])}</p></a>' for p in PAGES if p[1] in ("Tools", "Product")) + "</div>"
        elif slug == "guides":
            extra = '<div class="grid3">' + "".join(f'<a class="card link" href="{p[0]}.html"><h3>{E(p[3])}</h3><p>{E(p[4])}</p></a>' for p in PAGES if p[1] == "Guides") + "</div>"
        elif slug == "faq":
            extra = "".join(f"<details><summary>{E(p[8][0])}</summary><p>{E(p[8][1])}</p></details>" for p in PAGES)
        elif slug == "changelog":
            extra = '<div class="card"><h3>Version <span data-ver>-</span> <span class="muted" data-rel></span></h3><ul id="notes"><li>Loading&hellip;</li></ul></div>'
        elif slug == "privacy":
            extra = read_md("PRIVACY_POLICY.md")
        elif slug == "terms":
            extra = read_md("EULA.md")
        elif slug == "sitemap":
            groups = {}
            for s, t, _d, _k, g in ALL:
                groups.setdefault(g, []).append((s, t))
            extra = "".join(f"<h2>{E(g)}</h2><ul>" + "".join(f'<li><a href="{s}.html">{E(t)}</a></li>' for s, t in it) + "</ul>" for g, it in groups.items())
        ld = [APP_LD] if slug == "download" else []
        body = f'<section class="wrap page"><p class="eyebrow">{E(group)}</p><h1>{E(h1)}</h1><p class="lead">{E(desc)}</p>{extra}</section>'
        write(slug, head(title, desc, kw, slug, ld) + header() + body + footer())
    body = '<section class="wrap page"><h1>Page not found</h1><p class="lead">Try the search box above, or head <a href="index.html">home</a>.</p></section>'
    write("404", head("Not found - StegZ", "Page not found", "", "404") + header() + body + footer())


def main():
    os.makedirs(os.path.join(SITE, "assets"), exist_ok=True)
    for p in PAGES:
        build_page(p)
    build_index()
    build_static()
    urls = [("index", "1.0")] + [(s, "0.9" if s in ("download", "stegz", "steg", "stegs", "stegsz") else "0.7") for s, *_ in ALL]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for s, pr in urls:
        loc = f"{BASE}/" if s == "index" else f"{BASE}/{s}.html"
        sm += f"<url><loc>{loc}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>\n"
    with open(os.path.join(SITE, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sm + "</urlset>\n")
    with open(os.path.join(SITE, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    open(os.path.join(SITE, ".nojekyll"), "w").close()
    idx = [{"t": "StegZ - home", "u": "index.html", "d": "Hide, protect and compress files", "k": "stegz steg stegs stegsz stes home"}]
    idx += [{"t": h1, "u": f"{s}.html", "d": d, "k": k} for s, g, t, h1, d, k, *_ in PAGES]
    idx += [{"t": h1, "u": f"{s}.html", "d": d, "k": k} for s, g, t, h1, d, k in STATIC if s not in ("sitemap",)]
    idx.append({"t": "Site map", "u": "sitemap.html", "d": "Every page", "k": "sitemap pages index"})
    with open(os.path.join(SITE, "search-index.json"), "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False)
    # manifests: create once, never overwrite
    lj = os.path.join(SITE, "latest.json")
    if not os.path.exists(lj):
        with open(lj, "w", encoding="utf-8") as f:
            json.dump({"version": V.APP_VERSION, "released": TODAY, "mandatory": False, "min_check_interval": 1200,
                       "notes": ["First public release"],
                       "windows": {"url": f"{V.RELEASE_BASE}v{V.APP_VERSION}/{V.INSTALLER_NAME}", "sha256": "", "size": 0},
                       "android": {"url": "", "sha256": "", "size": 0}}, f, indent=2)
    aj = os.path.join(SITE, "announcement.json")
    if not os.path.exists(aj):
        with open(aj, "w", encoding="utf-8") as f:
            json.dump({"active": False, "id": "2026-launch", "title": "Welcome to StegZ", "message": "Thanks for using StegZ!",
                       "level": "info", "button": "", "url": "", "show_once": True,
                       "min_version": "", "max_version": "", "expires": ""}, f, indent=2)
    print(f"site generated: {len(PAGES) + len(STATIC) + 2} pages -> {SITE}")


if __name__ == "__main__":
    main()
