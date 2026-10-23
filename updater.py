"""StegZ update + announcement engine (no GUI code here, fully testable).

Rate-limit design (so GitHub never throttles us, even with huge user counts):
  * Only STATIC hosts are used (GitHub Pages, raw.githubusercontent, jsDelivr) -
    never api.github.com, so the 60-requests/hour API limit does not apply.
  * Conditional requests (ETag / If-None-Match): an unchanged file costs a tiny
    304 reply instead of a body.
  * Per-user jitter (+/-10%) so a million apps never fire in the same second.
  * Source order is shuffled per session -> load spreads over three CDNs, and any
    failing/429 source is skipped automatically with exponential back-off.
  * latest.json can raise "min_check_interval" remotely = a global throttle knob.
  * The installer itself downloads from GitHub Releases' CDN (no API, no limit).
"""
import datetime
import hashlib
import json
import os
import queue
import random
import ssl
import sys
import threading
import time
import urllib.error
import urllib.request

import version as V
from settings_store import local_data_dir

CHECK_INTERVAL = 20 * 60          # every 20 minutes while the app is open
MIN_INTERVAL = 5 * 60             # server may slow us, never below 5 min
HTTP_TIMEOUT = 12


def parse_version(v):
    out = []
    for part in str(v or "0").strip().lstrip("vV").split("-")[0].split("."):
        digits = "".join(ch for ch in part if ch.isdigit())
        out.append(int(digits or 0))
    while len(out) < 3:
        out.append(0)
    return tuple(out)


def is_newer(remote, local):
    return parse_version(remote) > parse_version(local)


def _installer_url(info):
    """Resolve the installer URL; locked to this project's GitHub releases."""
    win = info.get("windows") or {}
    ver = str(info.get("version", "")).lstrip("vV")
    url = win.get("url") or f"{V.RELEASE_BASE}v{ver}/{V.INSTALLER_NAME}"
    return url if url.startswith(V.RELEASE_BASE) else None


class UpdateManager:
    """Background thread. Talk to it via .events (queue) and .check_now()."""

    def __init__(self, settings, current_version=V.APP_VERSION):
        self.settings = settings
        self.current = current_version
        self.events = queue.Queue()
        self._wake = threading.Event()
        self._stop = threading.Event()
        self._etags = {}
        self._cache = {}
        self._backoff = 0
        self._interval = CHECK_INTERVAL
        self._last_check = 0.0
        self._busy_dl = False
        self.ready = None            # {"version","path","notes","mandatory"}
        self._failed = {}            # version -> time of last failed download
        self.updates_dir = os.path.join(local_data_dir(), "updates")
        os.makedirs(self.updates_dir, exist_ok=True)
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._order = list(V.MANIFEST_BASES)
        first = self._order[:2]
        random.shuffle(first)
        self._order = first + self._order[2:]

    # ---- public
    def start(self):
        self._cleanup_old()
        self._thread.start()

    def stop(self):
        self._stop.set()
        self._wake.set()

    def check_now(self, min_gap=60):
        """Ask for a check soon (throttled so focus-spam can't hammer anyone)."""
        if time.time() - self._last_check >= min_gap:
            self._wake.set()

    # ---- loop
    def _loop(self):
        while not self._stop.is_set():
            self._wake.clear()
            self._last_check = time.time()
            try:
                self._run_once()
            except Exception as e:  # never let the thread die
                self.events.put(("error", f"update check failed: {e}"))
            base = max(self._interval, MIN_INTERVAL)
            wait = base * random.uniform(0.9, 1.1) + self._backoff
            self._wake.wait(wait)

    def _run_once(self):
        ok_any = False
        ann = self._fetch("announcement.json")
        if ann is not None:
            ok_any = True
            self._handle_announcement(ann)
        info = self._fetch("latest.json")
        if info is not None:
            ok_any = True
            try:
                self._interval = max(int(info.get("min_check_interval", CHECK_INTERVAL)), MIN_INTERVAL)
            except (TypeError, ValueError):
                self._interval = CHECK_INTERVAL
            self._handle_latest(info)
        self._backoff = 0 if ok_any else min((self._backoff or 60) * 2, 3600)
        self.events.put(("checked", ok_any))

    # ---- fetching
    def _fetch(self, name):
        ctx = ssl.create_default_context()
        for base in self._order:
            url = base + name
            req = urllib.request.Request(url, headers={
                "User-Agent": f"StegZ/{self.current}",
                "Accept": "application/json",
                "Cache-Control": "no-cache",
                **({"If-None-Match": self._etags[url]} if url in self._etags and url in self._cache else {}),
            })
            try:
                with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT, context=ctx) as r:
                    body = r.read(1_000_000)
                    data = json.loads(body.decode("utf-8-sig"))
                    if r.headers.get("ETag"):
                        self._etags[url] = r.headers["ETag"]
                    self._cache[url] = data
                    return data
            except urllib.error.HTTPError as e:
                if e.code == 304 and url in self._cache:
                    return self._cache[url]
                if e.code in (429, 403):
                    try:
                        self._backoff = max(self._backoff, min(int(e.headers.get("Retry-After", 120)), 3600))
                    except (TypeError, ValueError):
                        self._backoff = max(self._backoff, 120)
            except (urllib.error.URLError, OSError, ValueError, json.JSONDecodeError):
                pass
        return None

    # ---- announcements
    def _handle_announcement(self, data):
        items = data.get("announcements") if isinstance(data, dict) and "announcements" in data else [data]
        now = datetime.datetime.now(datetime.timezone.utc)
        for a in items:
            if not isinstance(a, dict) or not a.get("active") or not (a.get("message") or a.get("title")):
                continue
            if str(a.get("platform", "all")).lower() not in ("all", "windows", "pc", "desktop"):
                continue
            ann_id = str(a.get("id") or hashlib.sha1(json.dumps(a, sort_keys=True).encode()).hexdigest()[:12])
            if a.get("show_once", True) and ann_id in self.settings.get("seen_announcements"):
                continue
            if a.get("min_version") and parse_version(self.current) < parse_version(a["min_version"]):
                continue
            if a.get("max_version") and parse_version(self.current) > parse_version(a["max_version"]):
                continue
            exp = a.get("expires")
            if exp:
                try:
                    e = datetime.datetime.fromisoformat(str(exp).replace("Z", "+00:00"))
                    if e.tzinfo is None:
                        e = e.replace(tzinfo=datetime.timezone.utc)
                    if now > e:
                        continue
                except ValueError:
                    pass
            a = dict(a)
            a["id"] = ann_id
            self.events.put(("announcement", a))
            return  # one popup at a time; next one shows after it is seen

    # ---- updates
    def _handle_latest(self, info):
        ver = str(info.get("version", ""))
        if not ver or not is_newer(ver, self.current):
            return
        if self.ready and self.ready["version"] == ver:
            return
        url = _installer_url(info)
        if not url:
            return
        win = info.get("windows") or {}
        meta = {"version": ver, "notes": info.get("notes", []), "mandatory": bool(info.get("mandatory"))}
        self.events.put(("update_available", dict(meta)))
        if not self.settings.get("auto_update") or self._busy_dl:
            return
        if time.time() - self._failed.get(ver, 0) < 3600:
            return
        self._download(ver, [url] + [m for m in win.get("mirrors", []) if str(m).startswith(V.RELEASE_BASE)],
                       (win.get("sha256") or "").lower(), meta)

    def _dest(self, ver):
        return os.path.join(self.updates_dir, f"StegZ-Setup-{ver}.exe")

    @staticmethod
    def _sha256_file(path):
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()

    def _download(self, ver, urls, sha, meta):
        self._busy_dl = True
        try:
            dest, part = self._dest(ver), self._dest(ver) + ".part"
            if os.path.exists(dest) and (not sha or self._sha256_file(dest) == sha):
                self._set_ready(ver, dest, meta)
                return
            for url in urls:
                try:
                    self._http_download(url, part)
                    if sha and self._sha256_file(part) != sha:
                        os.remove(part)
                        raise ValueError("checksum mismatch")
                    os.replace(part, dest)
                    self._set_ready(ver, dest, meta)
                    return
                except (OSError, ValueError, urllib.error.URLError):
                    continue
            self._failed[ver] = time.time()
            self.events.put(("download_failed", ver))
        finally:
            self._busy_dl = False

    def _http_download(self, url, part):
        have = os.path.getsize(part) if os.path.exists(part) else 0
        headers = {"User-Agent": f"StegZ/{self.current}"}
        if have:
            headers["Range"] = f"bytes={have}-"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT, context=ssl.create_default_context()) as r:
            if have and r.status != 206:      # server ignored Range -> restart
                have = 0
            total = have + int(r.headers.get("Content-Length") or 0)
            done = have
            last = 0.0
            with open(part, "ab" if have else "wb") as f:
                while True:
                    chunk = r.read(256 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    done += len(chunk)
                    if time.time() - last > 0.15:
                        last = time.time()
                        self.events.put(("download_progress", done, total))
            self.events.put(("download_progress", done, total))

    def _set_ready(self, ver, path, meta):
        self.ready = {**meta, "path": path}
        self.events.put(("update_ready", dict(self.ready)))

    def _cleanup_old(self):
        """Delete installers for versions we already run (or older), and stale parts."""
        try:
            for fn in os.listdir(self.updates_dir):
                if fn.startswith("StegZ-Setup-"):
                    v = fn[len("StegZ-Setup-"):].replace(".exe.part", "").replace(".exe", "")
                    if not is_newer(v, self.current):
                        os.remove(os.path.join(self.updates_dir, fn))
        except OSError:
            pass


def launch_installer(path):
    """Run the downloaded installer silently (one UAC prompt). True = launched."""
    if sys.platform != "win32":
        return False
    import ctypes
    args = "/SILENT /SUPPRESSMSGBOXES /NORESTART /CLOSEAPPLICATIONS"
    rc = ctypes.windll.shell32.ShellExecuteW(None, "runas", path, args, None, 1)
    return rc > 32
