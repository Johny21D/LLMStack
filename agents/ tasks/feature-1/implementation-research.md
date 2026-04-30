# Feature 1 — Daily Assignment Digest

## Summary

A once-a-day in-app notification sent to each Canvas student that tells them
how many assignments they still need to complete and which course each one
belongs to. The goal is to give students a single, predictable check-in each
day so they can plan their work without hunting through every course
individually.

## Problem

Canvas students are enrolled in multiple courses at once, and outstanding
assignments are scattered across each course's pages, modules, and the
to-do list. Students who don't visit every course every day can lose track
of what's due, especially when assignments come from courses they're not
actively working in that week. The existing global to-do list helps, but
it requires the student to actively go look. There's no daily, predictable
"here is what's on your plate" surface.

This feature addresses that gap by pushing a small, regular reminder into
the student's notification feed instead of waiting for the student to come
find the information.

## Who it's for

**Primary user:** Students enrolled in one or more Canvas courses.

**Why students specifically:** Instructors already have dashboards built
around course-level activity (SpeedGrader, gradebook, analytics).
Students are the ones whose work is fragmented across multiple courses,
and they're the ones most helped by an aggregated daily summary.

## What it does (user-visible behavior)

1. Once per day, every active student receives one in-app notification.
2. The notification states the total count of outstanding assignments
   the student has across all their courses.
3. The notification breaks the count down by course (e.g. "3 in
   Biology 101, 2 in English 210, 1 in Calculus").
4. The notification appears in Canvas's existing in-app notification
   feed — the same place students already see other Canvas notifications.
5. Students who have no outstanding assignments do not receive a
   notification that day (no empty digest).

## What it explicitly does not do (out of scope)

- **No email or push delivery.** In-app only. Email/push can be a future
  iteration, but adding them here multiplies the delivery, preference,
  and accessibility surface.
- **No instructor digest.** Students only.
- **No list of specific assignment names.** Counts and course names only.
  Listing every assignment turns this into a different feature (a
  cross-course to-do list) and raises FERPA-adjacent questions about
  what gets surfaced where.
- **No user-configurable schedule.** Fixed daily cadence, fixed delivery
  window. Per-user scheduling is a sensible v2.
- **No "recently graded" or "missing/overdue" callouts.** Just the count
  of work still to do.
- **No changes to how Canvas determines whether an assignment is
  outstanding.** The feature consumes that signal; it does not redefine it.

## Why this is the right size

- It is one scheduled job, one summary calculation, one notification
  template — small enough to actually finish.
- It touches enough of Canvas (users, enrollments, courses, assignments,
  notifications, background jobs) to make the design and research work
  meaningful.
- It has a real privacy surface (aggregating per-student data) without
  introducing new data sharing with third parties, which keeps the
  FERPA conversation focused.
- The boundary between "in" and "out" is unusually clean, which makes
  scope creep easy to spot and push back on.

## Success looks like

- Students who sign in regularly say the digest helps them catch
  assignments they would otherwise have missed.
- The job runs reliably each day across an institution-sized roster
  without degrading Canvas performance for other users.
- Students who want to turn it off can do so through Canvas's existing
  notification preferences.
- No student ever sees another student's data in their digest.

## Open questions to resolve in research

- What time of day should the digest run, and in whose time zone? (Canvas
  is multi-tenant and global.)
- Does Canvas's existing notification framework already support a
  "scheduled, aggregated, per-user" notification, or is this a new shape?
- How does the feature interact with students who are enrolled in dozens
  of courses (e.g. observers, TAs cross-listed as students)?
- What is the right behavior for unpublished courses, concluded courses,
  and assignments hidden from students?

These are tracked and answered in `implementation-research.md`.
