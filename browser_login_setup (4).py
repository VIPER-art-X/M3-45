#!/usr/bin/env python3
"""
One-time login / CAPTCHA setup for webpage_image_extractor.

Run this BY ITSELF, separately from the main extractor:

    python browser_login_setup.py

It opens a normal, visible browser window using the exact same saved
profile folder the main extractor's "mini browser" and "Log In / Clear
CAPTCHA" button use:

    ~/.webpage_image_extractor/chromium_profile

On exit it ALSO writes a session snapshot to
~/.webpage_image_extractor/search_state.json, which is what the headless
Automatic Search workers actually read (they can't open the profile
folder itself -- only one process can lock it at a time). Re-run this
script whenever those saved cookies go stale.

Note: a Google *account* login isn't needed for image search and isn't
necessarily a good idea -- what the search workers need is the ordinary
consent/session cookies, and a signed-in account gets challenged harder
(and can be locked) if Google sees automated traffic on it. Accept the
consent banner here; sign in only for sites that truly gate content
behind a login, like Pinterest.

Log into Pinterest, Google, or anywhere else you need to, exactly like
you would in any browser -- then just close the window. There's nothing
to click here and nothing to extract; the only job of this script is to
save cookies/login/session state into that shared profile so the main
extractor picks it up automatically from then on, without you needing to
log in or clear a CAPTCHA again.

Uses your real installed Google Chrome when it can find one, and falls
back to Playwright's bundled Chromium otherwise. Real Chrome tends to get
flagged as "automated" less often than the bundled build, which matters
for things like Google sign-in specifically refusing to work in a
detected-as-automated browser.

Requires: pip install playwright && playwright install chromium
"""
import os
import sys
import time
import json
import shutil

PROFILE_DIR = os.path.join(os.path.expanduser("~"), ".webpage_image_extractor", "chromium_profile")

# M3-157: Automatic Search runs several headless browsers at once, and a
# Chromium profile folder can only be locked by ONE process at a time --
# so the workers can't open PROFILE_DIR directly. Instead, this script
# writes a snapshot of the session (cookies + localStorage) here on exit,
# and each worker gets handed a copy of it. Without this file, logging in
# has no effect whatsoever on Automatic Search.
STATE_FILE = os.path.join(os.path.expanduser("~"), ".webpage_image_extractor", "search_state.json")

# Only these get wiped after you close the window -- Chromium's own HTTP/
# media disk cache plus browsing history. Cookies, Local Storage, and
# Login Data (i.e. the actual point of this script) are left alone, so
# the profile folder doesn't grow run over run but logins stay saved.
_CACHE_DIRS_TO_TRIM = ("Cache", "Code Cache", "GPUCache", "CacheStorage", "Service Worker")
_HISTORY_FILES_TO_TRIM = ("History", "History-journal", "Visited Links", "Top Sites",
                          "Top Sites-journal", "Network Action Predictor", "Shortcuts",
                          "Shortcuts-journal")


def _trim_cache():
    if not os.path.isdir(PROFILE_DIR):
        return
    for root, dirs, files in os.walk(PROFILE_DIR):
        for d in list(dirs):
            if d in _CACHE_DIRS_TO_TRIM:
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)
                dirs.remove(d)
        for f in files:
            if f in _HISTORY_FILES_TO_TRIM:
                try:
                    os.remove(os.path.join(root, f))
                except OSError:
                    pass


def _export_state(context):
    """Snapshots the logged-in session to STATE_FILE for the headless
    search workers. Called while the browser is still open -- storage_state()
    needs a live context."""
    try:
        state = context.storage_state()
    except Exception as e:
        print(f"(couldn't snapshot the session: {e})")
        return
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as fh:
            json.dump(state, fh)
        print(f"Session snapshot saved for Automatic Search "
              f"({len(state.get('cookies') or [])} cookie(s)): {STATE_FILE}")
    except Exception as e:
        print(f"(couldn't write {STATE_FILE}: {e})")


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright isn't installed -- run:\n"
              "  pip install playwright\n"
              "  playwright install chromium")
        sys.exit(1)

    os.makedirs(PROFILE_DIR, exist_ok=True)
    print(f"Profile folder: {PROFILE_DIR}")
    print("Opening a browser window -- log into Pinterest, Google, or whatever else you need.")
    print("When you're done, just close the window. Nothing needs to be clicked here.\n")

    with sync_playwright() as pw:
        common_kwargs = dict(
            headless=False,
            viewport=None,  # let the window size itself normally, like a real browser
            # Drop the "Chrome is being controlled by automated test
            # software" banner/flag -- this is part of what makes Google
            # and Pinterest refuse sign-in in an automated browser.
            ignore_default_args=["--enable-automation"],
            args=["--disable-blink-features=AutomationControlled",
                 "--window-size=1200,850"],
        )

        context = None
        try:
            context = pw.chromium.launch_persistent_context(
                PROFILE_DIR, channel="chrome", **common_kwargs)
            print("Using your installed Google Chrome.\n")
        except Exception:
            context = None

        if context is None:
            try:
                context = pw.chromium.launch_persistent_context(PROFILE_DIR, **common_kwargs)
                print("Google Chrome wasn't found -- using Playwright's bundled Chromium instead.\n")
            except Exception as e:
                print(f"Couldn't launch a browser at all: {e}\n"
                      "Run: playwright install chromium")
                sys.exit(1)

        page = context.pages[0] if context.pages else context.new_page()
        try:
            # Google Images rather than the Google home page: this is the
            # exact surface Automatic Search hits, so accepting the cookie/
            # consent banner here saves the consent cookies the headless
            # workers need. That banner alone is what most of the
            # "block/verification page" failures in the run log actually
            # were.
            page.goto("https://www.google.com/search?q=test&udm=2&hl=en&gl=us")
        except Exception as e:
            print(f"(page load warning: {e})")
        page.bring_to_front()

        print("Accept Google's cookie/consent banner if it appears, log into whatever")
        print("you need, then close the window when you're done...")
        last_snapshot = 0.0
        while context.pages:
            try:
                context.pages[0].wait_for_event("close", timeout=1000)
            except Exception:
                pass  # just a 1s poll timeout, not a real error -- keep waiting
            # Snapshot periodically as you go, so the session is captured
            # even if the window gets closed abruptly (storage_state()
            # needs a live context -- it can't be done after the fact).
            if context.pages and time.time() - last_snapshot > 10:
                last_snapshot = time.time()
                try:
                    _export_state(context)
                except Exception:
                    pass

        try:
            context.close()
        except Exception:
            pass

    _trim_cache()
    print("\nDone -- session saved. The main extractor (and its mini browser / "
          "\"Log In / Clear CAPTCHA\" button) will pick this up automatically next time.")


if __name__ == "__main__":
    main()
