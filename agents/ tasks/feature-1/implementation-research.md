# Feature 1 — Daily Assignment Digest

## Summary

A once-a-day notification sent to each Canvas student that tells them
how many assignments they still need to complete and which course each
one belongs to. The notification goes through Canvas's existing
notification framework, so delivery (in-app feed, mobile push, email)
follows each student's notification preferences. The goal is to give
students a single, predictable check-in each day so they can plan
their work without hunting through every course individually.

## Problem

Canvas students are enrolled in multiple courses at once, and outstanding
assignments are scattered across each course's pages, modules, and the
to-do list. Students who don't visit every course every day can lose
track of what's due, especially when assignments come from courses
they're not actively working in that week. The existing global to-do
list helps, but it requires the student to actively go look. There's
no predictable, push-style "here's what's on your plate today" surface.

This feature addresses that gap by sending a small, regular reminder
through Canvas's notification system instead of waiting for the student
to come find the information.

## Who it's for

**Primary user:** Students enrolled in one or more Canvas courses.

**Why students specifically:** Instructors already have dashboards built
around course-level activity (SpeedGrader, gradebook, analytics).
Students are the ones whose work is fragmented across multiple courses,
and they're the ones most helped by an aggregated daily summary.

## What it does (user-visible behavior)

1. Once per day, every active student receives one digest notification.
2. The notification states the total count of outstanding assignments
   the student has across all their courses.
3. The notification breaks the count down by course (e.g. "3 in
   Biology 101, 2 in English 210, 1 in Calculus").
4. The notification is created through Canvas's existing notification
   framework. **Where** it shows up — in-app notification feed, mobile
   push (for students with the Canvas Student app), email — is
   determined by each student's notification preferences, the same way
   every other Canvas notification works.
5. Students who have no outstanding assignments do not receive a
   notification that day (no empty digest).

## What it explicitly does not do (out of scope)

- **No new delivery channel.** The feature uses Canvas's existing
  notification framework. We do not build a parallel email pipeline,
  a custom push system, or SMS. Whatever channels Canvas already
  supports, this notification flows through; nothing more.
- **No instructor digest.** Students only.
- **No list of specific assignment names.** Counts and course names
  only. Listing every assignment turns this into a different feature
  (a cross-course to-do list) and raises FERPA-adjacent questions
  about what gets surfaced where.
- **No user-configurable schedule.** Fixed daily cadence, fixed
  delivery window. Per-user scheduling is a sensible v2.
- **No "recently graded" or "missing/overdue" callouts.** Just the
  count of work still to do.
- **No changes to how Canvas determines whether an assignment is
  outstanding.** The feature consumes that signal; it does not
  redefine it.
- **No new notification preference category** beyond what's needed to
  let students opt out. We reuse Canvas's existing preference UI, not
  a custom one.

## Why this is the right size

- It is one scheduled job, one summary calculation, and one new
  notification type plugged into existing infrastructure — small
  enough to actually finish.
- It touches enough of Canvas (users, enrollments, courses, assignments,
  notifications, background jobs) to make the design and research work
  meaningful.
- It has a real privacy surface (aggregating per-student data) without
  introducing new external data sharing, which keeps the FERPA
  conversation focused.
- The boundary between "in" and "out" is unusually clean, which makes
  scope creep easy to spot and push back on.

## Success looks like

- Students who sign in regularly say the digest helps them catch
  assignments they would otherwise have missed.
- Students who use the Canvas mobile app see the digest as a phone
  notification, without us having to build any phone-specific code.
- The job runs reliably each day across an institution-sized roster
  without degrading Canvas performance for other users.
- Students who want to turn it off can do so through Canvas's
  existing notification preferences.
- No student ever sees another student's data in their digest.

## Open questions to resolve in research

- What time of day should the digest run, and in whose time zone?
  (Canvas is multi-tenant and global.)
- How exactly does Canvas's notification framework model "scheduled,
  aggregated, per-user" notifications? Is this a new notification
  category, or does an existing category fit?
- How does the feature interact with students who are enrolled in
  dozens of courses (e.g. observers, TAs cross-listed as students)?
- What is the right behavior for unpublished courses, concluded
  courses, and assignments hidden from students?
- What's the right default delivery channel for students who haven't
  customized their notification preferences?

These are tracked and answered in `implementation-research.md`.
