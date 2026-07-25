use serde_json::Value;
use std::env;
use std::fs::{self, File, OpenOptions};
use std::io::{self, Read, Write};
use std::path::{Path, PathBuf};
use std::thread;
use std::time::{Duration, Instant};

const MAX_INPUT_BYTES: usize = 1024 * 1024;
const REMINDER: &str =
    "RELAY HANDOFF: threshold reached - run /relay:save via the Relay plugin, then continue.";

/// Process a Codex or Claude prompt-submit hook invocation.
///
pub fn run(args: &[String]) {
    let Some(agent) = parse_agent(args) else {
        return;
    };

    let mut input = Vec::new();
    let read_result = io::stdin()
        .take((MAX_INPUT_BYTES + 1) as u64)
        .read_to_end(&mut input);
    if read_result.is_err() {
        return;
    }

    let Some(state_dir) = hook_state_dir() else {
        return;
    };
    let store = CounterStore::new(state_dir);
    if let Some(reminder) = process_input(&input, agent, &store) {
        let _ = writeln!(io::stdout(), "{reminder}");
    }
}

fn parse_agent(args: &[String]) -> Option<&str> {
    for (index, arg) in args.iter().enumerate() {
        if arg == "--agent" {
            let agent = args.get(index + 1)?.as_str();
            return match agent {
                "codex" | "claude" => Some(agent),
                _ => None,
            };
        }
    }
    Some("codex")
}

fn process_input(input: &[u8], agent: &str, store: &CounterStore) -> Option<String> {
    if input.len() > MAX_INPUT_BYTES || !matches!(agent, "codex" | "claude") {
        return None;
    }
    let value = serde_json::from_slice::<Value>(input).ok()?;
    let event = value_string(
        value
            .get("event")
            .or_else(|| value.get("type"))
            .or_else(|| value.get("hook_event_name")),
    );
    if event != "UserPromptSubmit" {
        return None;
    }

    let mut session = value_string(
        value
            .get("session_id")
            .or_else(|| value.get("sessionId"))
            .or_else(|| value.get("session")),
    );
    if session.trim().is_empty() && agent == "codex" {
        session = value_string(value.get("cwd"));
    }
    if session.trim().is_empty() {
        return None;
    }

    reminder_for(store.increment(&session))
}

/// The reminder is owed only by a committed count; every other outcome is silent.
fn reminder_for(outcome: CounterOutcome) -> Option<String> {
    match outcome {
        CounterOutcome::Committed(count) if count % 10 == 0 => Some(REMINDER.to_owned()),
        _ => None,
    }
}

fn value_string(value: Option<&Value>) -> String {
    match value {
        Some(Value::String(value)) => value.clone(),
        Some(value) => value.to_string(),
        None => String::new(),
    }
}

fn hook_state_dir() -> Option<PathBuf> {
    #[cfg(windows)]
    let root = env::var_os("USERPROFILE");
    #[cfg(not(windows))]
    let root = env::var_os("HOME");
    let root = root.filter(|path| !path.is_empty())?;
    hook_state_dir_from_root(Path::new(&root))
}

fn hook_state_dir_from_root(root: &Path) -> Option<PathBuf> {
    if root.as_os_str().is_empty() || !root.is_absolute() {
        return None;
    }
    let canonical_root = fs::canonicalize(root).ok()?;
    let state_dir = canonical_root
        .join(".relay")
        .join(".semble")
        .join("hook-state");
    let mut builder = fs::DirBuilder::new();
    builder.recursive(true);
    #[cfg(unix)]
    {
        use std::os::unix::fs::DirBuilderExt;
        builder.mode(0o700);
    }
    builder.create(&state_dir).ok()?;
    let canonical_state_dir = fs::canonicalize(&state_dir).ok()?;
    if !canonical_state_dir.starts_with(&canonical_root) {
        return None;
    }
    let metadata = fs::metadata(&canonical_state_dir).ok()?;
    if !metadata.is_dir() {
        return None;
    }

    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;

        fs::set_permissions(&canonical_state_dir, fs::Permissions::from_mode(0o700)).ok()?;
        let mode = fs::metadata(&canonical_state_dir)
            .ok()?
            .permissions()
            .mode();
        if mode & 0o077 != 0 {
            return None;
        }
    }

    Some(canonical_state_dir)
}

struct HookLock(File);

impl Drop for HookLock {
    fn drop(&mut self) {
        let _ = self.0.unlock();
    }
}

/// How long an invocation waits for a contended session lock before it reports a
/// bounded failure. Contention is recoverable, so the wait is a time budget rather
/// than a fixed number of attempts.
const LOCK_WAIT_BUDGET: Duration = Duration::from_secs(10);

/// The first backoff step; the wait doubles up to `LOCK_WAIT_MAX_DELAY`.
const LOCK_WAIT_FIRST_DELAY: Duration = Duration::from_micros(200);

/// The longest single sleep between attempts.
const LOCK_WAIT_MAX_DELAY: Duration = Duration::from_millis(10);

fn lock_exclusive_within(path: &Path, budget: Duration) -> io::Result<HookLock> {
    let file = OpenOptions::new()
        .read(true)
        .write(true)
        .create(true)
        .truncate(false)
        .open(path)?;
    let deadline = Instant::now() + budget;
    let mut delay = LOCK_WAIT_FIRST_DELAY;
    loop {
        match file.try_lock() {
            Ok(()) => return Ok(HookLock(file)),
            Err(std::fs::TryLockError::WouldBlock) => {
                let remaining = deadline.saturating_duration_since(Instant::now());
                if remaining.is_zero() {
                    return Err(io::Error::new(
                        io::ErrorKind::WouldBlock,
                        "hook lock remained held for the whole wait budget",
                    ));
                }
                thread::sleep(delay.min(remaining));
                delay = (delay * 2).min(LOCK_WAIT_MAX_DELAY);
            }
            Err(std::fs::TryLockError::Error(error)) => return Err(error),
        }
    }
}

/// The explicit result of one counter update.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum CounterOutcome {
    /// The new count is published and durable.
    Committed(u64),
    /// Nothing was published; the previously published counter is intact.
    FailedBeforeReplacement(CounterFailure),
    /// The replacement happened but its durability barrier failed; the caller
    /// must reconcile the stored value before retrying.
    UncertainDurability { count: u64 },
}

/// Why an update failed before anything was published.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum CounterFailure {
    /// The session lock stayed held for the whole bounded wait.
    LockUnavailable,
    /// The existing counter could not be read.
    UnreadableCounter,
    /// The existing counter was not a count; it is reported, never reset.
    MalformedCounter,
    /// The count cannot advance without wrapping.
    Overflow,
    /// The atomic replacement failed before publishing the new value.
    WriteFailed,
}

/// Map an atomic-write stage failure onto the counter contract.
fn outcome_for_write_stage(stage: crate::atomic_io::WriteStage, count: u64) -> CounterOutcome {
    match stage {
        crate::atomic_io::WriteStage::Prepare | crate::atomic_io::WriteStage::Replace => {
            CounterOutcome::FailedBeforeReplacement(CounterFailure::WriteFailed)
        }
        crate::atomic_io::WriteStage::ParentSync => CounterOutcome::UncertainDurability { count },
    }
}

struct CounterStore {
    state_dir: PathBuf,
}

/// Move unparseable counter content aside so the reset leaves evidence behind.
fn quarantine_counter(counter: &Path) -> io::Result<()> {
    let quarantine = counter.with_file_name(format!(
        "{}.corrupt",
        counter
            .file_name()
            .map(|name| name.to_string_lossy().into_owned())
            .unwrap_or_else(|| "relay-hook.count".to_owned())
    ));
    match fs::remove_file(&quarantine) {
        Ok(()) => {}
        Err(error) if error.kind() == io::ErrorKind::NotFound => {}
        Err(error) => return Err(error),
    }
    fs::rename(counter, &quarantine)
}

impl CounterStore {
    fn new(state_dir: PathBuf) -> Self {
        Self { state_dir }
    }

    fn increment(&self, session: &str) -> CounterOutcome {
        let hash = session_hash(session);
        let counter = self.state_dir.join(format!("relay-hook-{hash}.count"));
        let lock = self.state_dir.join(format!("relay-hook-{hash}.lock"));
        let Ok(_guard) = lock_exclusive_within(&lock, LOCK_WAIT_BUDGET) else {
            return CounterOutcome::FailedBeforeReplacement(CounterFailure::LockUnavailable);
        };
        let current = match fs::read_to_string(&counter) {
            Ok(value) => match value.trim().parse::<u64>() {
                Ok(current) => current,
                // A counter that is not a count has no prior value to preserve. The
                // unparseable content is quarantined as evidence instead of being
                // overwritten, so the reset is observable rather than silent, and the
                // session keeps counting instead of wedging its reminders forever.
                Err(_) => match quarantine_counter(&counter) {
                    Ok(()) => 0,
                    Err(_) => {
                        return CounterOutcome::FailedBeforeReplacement(
                            CounterFailure::MalformedCounter,
                        )
                    }
                },
            },
            Err(error) if error.kind() == io::ErrorKind::NotFound => 0,
            Err(_) => {
                return CounterOutcome::FailedBeforeReplacement(CounterFailure::UnreadableCounter)
            }
        };
        let Some(next) = current.checked_add(1) else {
            return CounterOutcome::FailedBeforeReplacement(CounterFailure::Overflow);
        };
        let contents = next.to_string();
        match crate::atomic_io::write_atomic_staged(&counter, contents.as_bytes()) {
            Ok(()) => CounterOutcome::Committed(next),
            Err(error) => outcome_for_write_stage(error.stage, next),
        }
    }
}

fn session_hash(session: &str) -> u64 {
    session.bytes().fold(0u64, |hash, byte| {
        hash.wrapping_mul(131).wrapping_add(byte as u64)
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::{AtomicU64, Ordering};
    use std::sync::{Arc, Barrier};
    use std::time::{SystemTime, UNIX_EPOCH};

    struct TestTempDir {
        root: PathBuf,
        path: PathBuf,
    }

    static TEST_ROOT_SEQUENCE: AtomicU64 = AtomicU64::new(0);

    impl TestTempDir {
        fn new() -> Self {
            let suffix = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos();
            let sequence = TEST_ROOT_SEQUENCE.fetch_add(1, Ordering::Relaxed);
            let process = std::process::id();
            let root = env::temp_dir().join(format!(
                "relay-hook-test-{process}-{sequence}-{suffix}"
            ));
            fs::create_dir(&root).unwrap();
            let path = hook_state_dir_from_root(&root).unwrap();
            Self { root, path }
        }
    }

    impl Drop for TestTempDir {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.root);
        }
    }

    fn input(event: &str, session: &str) -> Vec<u8> {
        format!(r#"{{"event":"{event}","session_id":"{session}"}}"#).into_bytes()
    }

    #[test]
    fn state_dir_creation_failure_is_silent() {
        let temp = TestTempDir::new();
        let root_file = temp.root.join("not-a-directory");
        fs::write(&root_file, b"").unwrap();
        assert_eq!(hook_state_dir_from_root(&root_file), None);
    }

    #[cfg(unix)]
    #[test]
    fn state_dir_symlink_escape_is_silent() {
        use std::os::unix::fs::symlink;

        let temp = TestTempDir::new();
        fs::remove_dir_all(&temp.path).unwrap();
        let outside = temp.root.with_extension("outside");
        fs::create_dir(&outside).unwrap();
        let link = temp.root.join(".relay").join(".semble").join("hook-state");
        symlink(&outside, &link).unwrap();
        assert_eq!(hook_state_dir_from_root(&temp.root), None);
        fs::remove_dir_all(outside).unwrap();
    }

    #[cfg(unix)]
    #[test]
    fn state_dir_is_owner_only() {
        use std::os::unix::fs::PermissionsExt;

        let temp = TestTempDir::new();
        let mode = fs::metadata(&temp.path).unwrap().permissions().mode();
        assert_eq!(mode & 0o077, 0);
    }

    #[test]
    fn test_roots_are_unique_under_parallel_creation() {
        const THREADS: usize = 16;
        let barrier = Arc::new(Barrier::new(THREADS));
        let mut workers = Vec::new();
        for _ in 0..THREADS {
            let barrier = Arc::clone(&barrier);
            workers.push(std::thread::spawn(move || {
                barrier.wait();
                TestTempDir::new()
            }));
        }
        let mut roots = Vec::new();
        let mut panics = 0;
        for worker in workers {
            match worker.join() {
                Ok(temp) => roots.push(temp),
                Err(_) => panics += 1,
            }
        }
        assert_eq!(panics, 0, "test root creation panicked");
        let unique = roots
            .iter()
            .map(|temp| temp.root.clone())
            .collect::<std::collections::HashSet<_>>();
        assert_eq!(unique.len(), THREADS, "test roots collided");
    }

    #[test]
    fn absent_counter_commits_first_turn() {
        let temp = TestTempDir::new();
        let store = CounterStore::new(temp.path.clone());
        assert_eq!(store.increment("fresh"), CounterOutcome::Committed(1));
    }

    #[test]
    fn existing_counter_commits_next_value() {
        let temp = TestTempDir::new();
        let store = CounterStore::new(temp.path.clone());
        let counter = temp
            .path
            .join(format!("relay-hook-{}.count", session_hash("existing")));
        fs::write(&counter, b"7").unwrap();
        assert_eq!(store.increment("existing"), CounterOutcome::Committed(8));
        assert_eq!(fs::read_to_string(&counter).unwrap(), "8");
    }

    #[test]
    fn malformed_counter_is_quarantined_before_counting_restarts() {
        let temp = TestTempDir::new();
        let store = CounterStore::new(temp.path.clone());
        let counter = temp
            .path
            .join(format!("relay-hook-{}.count", session_hash("malformed")));
        let quarantine = temp
            .path
            .join(format!("relay-hook-{}.count.corrupt", session_hash("malformed")));
        fs::write(&counter, b"eighty-seven").unwrap();
        assert_eq!(store.increment("malformed"), CounterOutcome::Committed(1));
        assert_eq!(fs::read_to_string(&counter).unwrap(), "1");
        assert_eq!(
            fs::read_to_string(&quarantine).unwrap(),
            "eighty-seven",
            "the unparseable content must survive as evidence of the reset"
        );
    }

    #[test]
    fn unreadable_counter_is_reported() {
        let temp = TestTempDir::new();
        let store = CounterStore::new(temp.path.clone());
        let counter = temp
            .path
            .join(format!("relay-hook-{}.count", session_hash("unreadable")));
        fs::create_dir(&counter).unwrap();
        assert_eq!(
            store.increment("unreadable"),
            CounterOutcome::FailedBeforeReplacement(CounterFailure::UnreadableCounter)
        );
        assert!(counter.is_dir());
    }

    /// A published counter must survive a replacement that never happens.
    #[cfg(windows)]
    #[test]
    fn blocked_replacement_preserves_published_counter() {
        use std::os::windows::fs::OpenOptionsExt;

        const FILE_SHARE_READ: u32 = 1;

        let temp = TestTempDir::new();
        let store = CounterStore::new(temp.path.clone());
        let counter = temp
            .path
            .join(format!("relay-hook-{}.count", session_hash("blocked-write")));
        fs::write(&counter, b"41").unwrap();
        let holder = OpenOptions::new()
            .read(true)
            .share_mode(FILE_SHARE_READ)
            .open(&counter)
            .unwrap();
        assert_eq!(
            store.increment("blocked-write"),
            CounterOutcome::FailedBeforeReplacement(CounterFailure::WriteFailed)
        );
        assert_eq!(fs::read_to_string(&counter).unwrap(), "41");
        drop(holder);
        assert_eq!(
            store.increment("blocked-write"),
            CounterOutcome::Committed(42)
        );
    }

    /// A published counter must survive a temporary file that cannot be created.
    #[cfg(unix)]
    #[test]
    fn blocked_replacement_preserves_published_counter() {
        use std::os::unix::fs::PermissionsExt;

        let temp = TestTempDir::new();
        let store = CounterStore::new(temp.path.clone());
        let counter = temp
            .path
            .join(format!("relay-hook-{}.count", session_hash("blocked-write")));
        fs::write(&counter, b"41").unwrap();
        let lock = temp
            .path
            .join(format!("relay-hook-{}.lock", session_hash("blocked-write")));
        fs::write(&lock, b"").unwrap();
        fs::set_permissions(&temp.path, fs::Permissions::from_mode(0o500)).unwrap();
        let outcome = store.increment("blocked-write");
        fs::set_permissions(&temp.path, fs::Permissions::from_mode(0o700)).unwrap();
        assert_eq!(
            outcome,
            CounterOutcome::FailedBeforeReplacement(CounterFailure::WriteFailed)
        );
        assert_eq!(fs::read_to_string(&counter).unwrap(), "41");
        assert_eq!(
            store.increment("blocked-write"),
            CounterOutcome::Committed(42)
        );
    }

    #[test]
    fn saturated_counter_reports_overflow_and_preserves_state() {
        let temp = TestTempDir::new();
        let store = CounterStore::new(temp.path.clone());
        let counter = temp
            .path
            .join(format!("relay-hook-{}.count", session_hash("saturated")));
        fs::write(&counter, u64::MAX.to_string().as_bytes()).unwrap();
        assert_eq!(
            store.increment("saturated"),
            CounterOutcome::FailedBeforeReplacement(CounterFailure::Overflow)
        );
        assert_eq!(
            fs::read_to_string(&counter).unwrap(),
            u64::MAX.to_string()
        );
    }

    #[test]
    fn write_stages_map_to_distinct_outcomes() {
        assert_eq!(
            outcome_for_write_stage(crate::atomic_io::WriteStage::Prepare, 4),
            CounterOutcome::FailedBeforeReplacement(CounterFailure::WriteFailed)
        );
        assert_eq!(
            outcome_for_write_stage(crate::atomic_io::WriteStage::Replace, 4),
            CounterOutcome::FailedBeforeReplacement(CounterFailure::WriteFailed)
        );
        assert_eq!(
            outcome_for_write_stage(crate::atomic_io::WriteStage::ParentSync, 4),
            CounterOutcome::UncertainDurability { count: 4 }
        );
    }

    #[test]
    fn only_committed_counts_emit_the_reminder() {
        assert_eq!(reminder_for(CounterOutcome::Committed(10)).as_deref(), Some(REMINDER));
        assert_eq!(reminder_for(CounterOutcome::Committed(11)), None);
        assert_eq!(
            reminder_for(CounterOutcome::UncertainDurability { count: 20 }),
            None
        );
        assert_eq!(
            reminder_for(CounterOutcome::FailedBeforeReplacement(
                CounterFailure::LockUnavailable
            )),
            None
        );
    }

    #[test]
    fn contended_lock_waits_and_then_commits() {
        let temp = TestTempDir::new();
        let lock_path = temp
            .path
            .join(format!("relay-hook-{}.lock", session_hash("held")));
        let barrier = Arc::new(Barrier::new(2));
        let holder_barrier = Arc::clone(&barrier);
        let holder_path = lock_path.clone();
        let holder = std::thread::spawn(move || {
            let guard = lock_exclusive_within(&holder_path, LOCK_WAIT_BUDGET).unwrap();
            holder_barrier.wait();
            std::thread::sleep(std::time::Duration::from_millis(300));
            drop(guard);
        });
        barrier.wait();
        let started = std::time::Instant::now();
        assert_eq!(
            CounterStore::new(temp.path.clone()).increment("held"),
            CounterOutcome::Committed(1),
            "recoverable contention must never lose a submission"
        );
        assert!(started.elapsed() >= std::time::Duration::from_millis(250));
        assert!(started.elapsed() < LOCK_WAIT_BUDGET);
        holder.join().unwrap();
    }

    #[test]
    fn lock_held_past_the_budget_reports_lock_unavailable() {
        let temp = TestTempDir::new();
        let lock_path = temp
            .path
            .join(format!("relay-hook-{}.lock", session_hash("blocked")));
        let barrier = Arc::new(Barrier::new(2));
        let holder_barrier = Arc::clone(&barrier);
        let holder_path = lock_path.clone();
        let holder = std::thread::spawn(move || {
            let guard = lock_exclusive_within(&holder_path, LOCK_WAIT_BUDGET).unwrap();
            holder_barrier.wait();
            std::thread::sleep(std::time::Duration::from_millis(200));
            drop(guard);
        });
        barrier.wait();
        let budget = std::time::Duration::from_millis(20);
        let started = std::time::Instant::now();
        let outcome = lock_exclusive_within(&lock_path, budget);
        assert!(
            outcome.is_err(),
            "a lock held past the budget must report a bounded failure"
        );
        assert!(started.elapsed() < std::time::Duration::from_millis(500));
        holder.join().unwrap();
    }

    #[test]
    fn distinct_sessions_do_not_interfere() {
        let temp = TestTempDir::new();
        let store = CounterStore::new(temp.path.clone());
        let first = "session-alpha";
        let second = "session-beta";
        assert_ne!(session_hash(first), session_hash(second));
        let lock_path = temp
            .path
            .join(format!("relay-hook-{}.lock", session_hash(first)));
        let held = lock_exclusive_within(&lock_path, LOCK_WAIT_BUDGET).unwrap();
        assert_eq!(store.increment(second), CounterOutcome::Committed(1));
        drop(held);
        assert_eq!(store.increment(first), CounterOutcome::Committed(1));
    }

    #[test]
    fn irrelevant_input_is_silent_noop() {
        let temp = TestTempDir::new();
        let store = CounterStore::new(temp.path.clone());
        assert_eq!(
            process_input(&input("SessionStart", "session"), "codex", &store),
            None
        );
        assert!(fs::read_dir(&temp.path).unwrap().next().is_none());
    }
    #[test]
    fn reminder_occurs_on_every_tenth_turn() {
        let temp = TestTempDir::new();
        let store = CounterStore::new(temp.path.clone());
        let args = input("UserPromptSubmit", "session");
        for turn in 1..=20 {
            let reminder = process_input(&args, "codex", &store);
            if turn % 10 == 0 {
                assert_eq!(reminder.as_deref(), Some(REMINDER));
            } else {
                assert_eq!(reminder, None);
            }
        }
    }

    #[test]
    fn oversize_input_is_silent_noop() {
        let temp = TestTempDir::new();
        let store = CounterStore::new(temp.path.clone());
        let input = vec![b' '; MAX_INPUT_BYTES + 1];
        assert_eq!(process_input(&input, "codex", &store), None);
        assert!(fs::read_dir(&temp.path).unwrap().next().is_none());
    }
    /// The expected total is derived from the reported outcomes, so the check does
    /// not depend on a chosen worker count or a hardcoded counter value.
    fn run_concurrent_session(workers: usize, session: &'static str) -> (Vec<CounterOutcome>, u64) {
        let temp = Arc::new(TestTempDir::new());
        let barrier = Arc::new(Barrier::new(workers));
        let mut handles = Vec::new();
        for _ in 0..workers {
            let temp = Arc::clone(&temp);
            let barrier = Arc::clone(&barrier);
            handles.push(std::thread::spawn(move || {
                let store = CounterStore::new(temp.path.clone());
                barrier.wait();
                store.increment(session)
            }));
        }
        let outcomes = handles
            .into_iter()
            .map(|handle| handle.join().unwrap())
            .collect::<Vec<_>>();
        let counter = temp
            .path
            .join(format!("relay-hook-{}.count", session_hash(session)));
        let persisted = fs::read_to_string(&counter)
            .unwrap()
            .trim()
            .parse::<u64>()
            .unwrap();
        (outcomes, persisted)
    }

    #[test]
    fn concurrent_increments_are_not_lost() {
        for workers in [2usize, 5, 16, 33] {
            let (outcomes, persisted) = run_concurrent_session(workers, "concurrent-session");
            let committed = outcomes
                .iter()
                .filter(|outcome| matches!(outcome, CounterOutcome::Committed(_)))
                .count();
            let failed = outcomes
                .iter()
                .filter(|outcome| !matches!(outcome, CounterOutcome::Committed(_)))
                .count();
            assert_eq!(
                failed, 0,
                "recoverable contention reported {failed} failures at {workers} workers: {outcomes:?}"
            );
            assert_eq!(
                persisted, committed as u64,
                "persisted count must equal the committed submissions at {workers} workers"
            );
            let mut counts = outcomes
                .iter()
                .filter_map(|outcome| match outcome {
                    CounterOutcome::Committed(count) => Some(*count),
                    _ => None,
                })
                .collect::<Vec<_>>();
            counts.sort_unstable();
            counts.dedup();
            assert_eq!(
                counts.len(),
                committed,
                "each committed submission must observe a distinct count"
            );
        }
    }

    #[test]
    fn reminders_follow_committed_tenth_turns() {
        for start in [0u64, 5, 9, 17, 95] {
            let temp = TestTempDir::new();
            let store = CounterStore::new(temp.path.clone());
            let session = "boundary-session";
            let counter = temp
                .path
                .join(format!("relay-hook-{}.count", session_hash(session)));
            if start > 0 {
                fs::write(&counter, start.to_string().as_bytes()).unwrap();
            }
            let args = input("UserPromptSubmit", session);
            for step in 1..=25u64 {
                let reminder = process_input(&args, "codex", &store);
                let count = start + step;
                if count % 10 == 0 {
                    assert_eq!(
                        reminder.as_deref(),
                        Some(REMINDER),
                        "missing reminder at committed count {count}"
                    );
                } else {
                    assert_eq!(reminder, None, "unexpected reminder at count {count}");
                }
            }
        }
    }
}
