# Static Preview Banner Removal

- Removed the injected yellow static-preview notice from `js/demo-forms.js`.
- Kept the static preview authentication bridge: login/signup submissions still forward to Django on port 8000.
- Rebuilt the generated `site/` directory using `build_static.py`.
- Added `FIX_STATIC_PREVIEW_BANNER.bat` for repeatable local rebuilds.

This removes the notice from the static preview. It does not make port 5500 a Django backend or make authentication work while Django is stopped. The real application remains `http://127.0.0.1:8000/`.

To apply on Windows, run `FIX_STATIC_PREVIEW_BANNER.bat` from the project root. Then hard-refresh the static preview (Ctrl+Shift+R). For real sign-in, start Django with `START_TALENTBRIDGEAI.bat`.
