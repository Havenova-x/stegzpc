StegZ website update - Android download button
==============================================
1. Unzip this over your DESKTOP project folder (StegZ), letting it overwrite files:
     site\ , tools\gen_site.py , updater.py , docs\PRIVACY_POLICY.md
2. Commit + push with GitHub Desktop (the desktop/public repo, Havenova-x/stegzpc). Vercel redeploys by itself.
3. The page shows "Android version: coming soon" until the mobile build publishes site\android.json.
   After that the Android button appears automatically - nothing else to do.
4. When the first Android build is live, open site\announcement.json and change the Android item to "active": true, then push.
   (Windows and Android each only show their own announcement. The next desktop build also ignores Android items.)
