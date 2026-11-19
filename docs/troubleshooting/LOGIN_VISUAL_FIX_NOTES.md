# Login page visual fix

- Fixed the login header stacking so the navigation remains above the login card.
- Added responsive layout rules for desktop, tablet, and mobile.
- Styled the Google OAuth notice as a compact information panel rather than unformatted text.
- Kept the existing login fields, Google button, visual panel, and animated ambient background.

Google sign-in remains disabled until valid Google OAuth Client ID and Client Secret are configured in the server `.env`. This is an external credential requirement, not a CSS or HTML bug. Email/password sign-in remains available.

Validation performed: ZIP integrity and Python syntax checks. A live browser/Django login test was not available in this environment.
