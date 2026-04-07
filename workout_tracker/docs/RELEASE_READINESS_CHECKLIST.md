# Workout Tracker Release Readiness Checklist

Target release window: personal iPhone PWA beta

## Day 1: Core Reliability

- [x] Verify Program page button wiring after SPA navigation
- [x] Fix Program page global handlers for inline button actions
- [x] Smoke test backend APIs with authenticated test client:
  - [x] Program create/day/exercise/add/remove/delete
  - [x] Workout create/list/delete
  - [x] Nutrition profile save + meal create/list/delete
- [ ] Manual UI pass in browser:
  - [ ] Programs: Add Program, Add Day, Add Exercise, Remove/Delete actions
  - [ ] Tracker: Save Workout, Delete Workout, Load from plan
  - [ ] Nutrition: Save profile, Log meal, Delete meal, Save/Use/Delete saved meal

## Day 2: Production Safety

- [x] Add production-safe session cookie settings
  - [x] SESSION_COOKIE_SECURE
  - [x] SESSION_COOKIE_HTTPONLY
  - [x] SESSION_COOKIE_SAMESITE
- [x] Confirm SECRET_KEY and DATABASE_URL are env-only in production
- [x] Add basic auth rate limiting for login endpoint

## Day 3: Data + Deployment Baseline

- [x] Move deployment DB from SQLite to Postgres
- [x] Add startup/migration instructions for hosted environment
- [x] Add backup/export command for user data (CSV or JSON)

## Day 4: iPhone PWA Foundation

- [x] Add manifest.json with name, theme_color, display: standalone
- [x] Add service worker for app shell caching
- [x] Add offline fallback page
- [x] Add iOS home-screen meta tags (apple-mobile-web-app-*) and 180x180 icon

## Day 5: AI Resilience

- [x] Hercules returns up to 3 personalised tips per request (priority-ranked)
- [x] Dashboard auto-loads tips on page mount (no button press required)
- [x] Tip carousel (← / →) to cycle through all returned insights
- [x] Weekly check-in panel with headline, narrative, and next-step list
- [x] Inline form cue shown when exercise is selected in Tracker
- [x] Post-workout Hercules insight shown after each Save Workout action
- [x] Add timeout handling for AI endpoints (5 s hard limit)
- [x] Add fallback message paths in UI if AI provider is unavailable
- [x] Add server logging for AI failures

## Day 6: Missing Feature Gaps (pre-release must-haves)

- [x] Body metrics UI — BodyMetric model exists in DB but is not surfaced
- [x] Rest timer — in-session countdown between sets
- [x] Goal tracking — let users set a target lift or bodyweight; Hercules tracks progress toward it
- [x] Calendar / history view — browse sessions by date

## Day 7: Real Device Beta

- [ ] Deploy HTTPS build
- [ ] Install to iPhone via Add to Home Screen
- [ ] Run 2-3 days of real usage
- [ ] Fix only blockers and high-friction issues
- [ ] Freeze scope and cut release

## Notes

- API smoke test status: PASS (program/tracker/nutrition core CRUD)
- Known fixed issue: Program page inline button handlers after SPA navigation
- Hercules AI proactivity improvements merged: multi-tip engine, auto-load, weekly summary, form cues, post-workout feedback
