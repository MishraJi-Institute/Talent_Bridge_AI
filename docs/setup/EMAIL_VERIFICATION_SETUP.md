# TalentBridge AI email verification

Email verification is temporarily disabled. New email/password registrations can sign in immediately, and signup does not send a verification email. Existing unverified email/password accounts are activated after a successful password check at sign-in. Accounts disabled for other reasons remain inactive.

The verification model, signed-link handler, and email-sending helper are retained for future development. The resend-verification route currently redirects to sign-in without changing accounts or sending mail.

When verification is implemented, configure inbox delivery in the private `TalentBridgeAI/.env` file (never commit or share it):

```dotenv
DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-sending-address@gmail.com
EMAIL_HOST_PASSWORD=your-provider-app-password
EMAIL_USE_TLS=true
DEFAULT_FROM_EMAIL=TalentBridge AI <your-sending-address@gmail.com>
```

Re-enabling verification will also require restoring the relevant signup, sign-in, and allauth verification gates. Verification links are signed, tied to the user's ID and email, and expire after 24 hours.
