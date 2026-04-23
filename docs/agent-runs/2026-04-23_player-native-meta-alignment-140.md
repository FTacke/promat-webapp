# 2026-04-23 Player Native Meta Alignment

- Corrected the productive player summary-card builder so `native_speaker` sessions no longer reuse learner-specific rows like `Sprachaufenthalte` and `Explorator:in`.
- Kept the player card shell neutral and badges unchanged; only the native facts block now follows the existing speaker-card pattern with translated `Standardvarietät`, optional distinct origin country, `Herkunftsregion`, `Geschlecht`, and `Aufnahmejahr`.
- Updated the active player spec to remove the overgeneralized shared-facts rule and added a focused regression in `app/tests/test_research_sessions.py` for the compare case with a native secondary card.