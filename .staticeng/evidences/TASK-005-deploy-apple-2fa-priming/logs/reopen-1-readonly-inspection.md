# TASK-005 Reopen 1 Read-Only Inspection

## Scope
- Read-only verification after the user reported no iPhone trusted-device popup after `/auth`.
- No Docker service/config/cookie/keyring/source mutations were performed.
- Live log excerpts were sanitized before analysis; account identifiers, URLs, tokens, cookies, session values, and MFA codes are omitted.

## Sanitized Live Log Findings
- `/auth` reached the live container at 2026-05-30 00:22:53 and 2026-05-30 00:23:44.
- The first `/auth` restarted the pending MFA loop, forced a fresh login flow, removed local auth files as designed by the deployed `/auth` implementation, completed password authentication, entered HSA2, and requested an authentication code via Telegram.
- No priming warning was logged, so `get_trusted_phone_numbers()` did not raise an exception on that first fresh flow.
- No explicit log line confirms Apple sent a trusted-device challenge. Current TASK-004 instrumentation only logs priming failures, not successful Apple response status/details.
- The second `/auth` forced another fresh login less than one minute later and Apple returned an invalid credential/throttle sequence, followed by temporary refusal messages.

## Code Inspection Findings
- `request_2fa_telegram()` calls `icloud.get_trusted_phone_numbers()` before `telegram_bot.request_auth_code()`, but does not trigger SMS and does not log the number of trusted phone numbers returned.
- `get_trusted_phone_numbers()` builds `GET https://idmsa.apple.com/appleauth/auth` with OAuth headers and parses `direct.twoSV.phoneNumberVerification.trustedPhoneNumbers` from HTML boot args.
- The parser does not inspect an alternate `direct.twoSV.bridgeInitiateData.phoneNumberVerification.trustedPhoneNumbers` shape, so a current Apple response using that shape would look like a successful request with zero parsed SMS choices.
- The only HSA2 trusted-device verification endpoint present is `POST /appleauth/auth/verify/trusteddevice/securitycode`, used to validate an already-displayed trusted-device code.
- No explicit `send` or `challenge` method exists for trusted-device popup delivery beyond the implicit HSA2 flow and the trusted-phone lookup.
- SMS fallback endpoints are implemented as `PUT /appleauth/auth/verify/phone` and `POST /appleauth/auth/verify/phone/securitycode`, but Telegram auth does not currently expose a user choice to select an SMS device.

## Recommendation
- Next safest product path: add sanitized instrumentation around the priming call and trusted-phone parsing first, then add an explicit SMS fallback path requiring user choice when no trusted-device popup arrives, reusing existing `get_trusted_phone_numbers()`, `send_2fa_code_sms()`, and `validate_2fa_code_sms()` APIs.
- Include parser coverage for the alternate trusted-phone response shape if instrumentation or upstream comparison confirms Apple is returning it.
- Do not auto-send SMS. Make it an explicit Telegram action/choice because SMS may have user-visible side effects and could incur carrier/account effects.
- Treat an explicit trusted-device popup endpoint as not currently available in this codebase; implementing one would require verified Apple endpoint behavior or controlled instrumentation first.
