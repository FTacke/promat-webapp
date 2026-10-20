#!/usr/bin/env python3
"""Self-test for vm_storage_vscode_cleanup.py. Runs against throw-away fixtures only.

Usage: vm_storage_vscode_cleanup_selftest.py [path-to-cleanup-script]

Needs Linux; run as root to cover the "unreadable process table" and the
"deletion fails" cases (they are skipped otherwise).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

SCRIPT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "vm_storage_vscode_cleanup.py")
DAY = 86400
NOW = time.time()
results = []


def h(n):  # deterministic 40-hex commit from a small int
    return f"{n:040x}"


def make(servers, channel, n, version, age_days, complete=True, staging=False, with_pkg=True, pad=25):
    name = f"{channel}-{h(n)}" + (".staging" if staging else "")
    root = os.path.join(servers, name)
    srv = os.path.join(root, "server")
    os.makedirs(os.path.join(srv, "bin"))
    os.makedirs(os.path.join(srv, "out"))
    os.makedirs(os.path.join(srv, "extensions"))
    os.makedirs(os.path.join(srv, "node_modules"))
    if with_pkg:
        json.dump({"version": version}, open(os.path.join(srv, "package.json"), "w"))
    if complete:
        open(os.path.join(srv, "node"), "w").write("x" * 4096)
        open(os.path.join(srv, "bin", "code-server"), "w").write("#!/bin/sh\n")
        open(os.path.join(srv, "out", "server-main.js"), "w").write("// js\n")
        json.dump({"version": version}, open(os.path.join(srv, "product.json"), "w"))
    for i in range(pad if complete else 0):  # a real install holds thousands of files
        open(os.path.join(srv, "node_modules", f"mod{i}.js"), "w").write("//")
    t = NOW - age_days * DAY
    for p in (srv, root):
        os.utime(p, (t, t))
    return root


def run(servers, *extra, user=None, lock=None, env=None):
    cmd = [sys.executable, SCRIPT, "--servers-dir", servers, "--format", "json", "--active-grace-minutes", "0",
           "--lock-file", lock or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(servers))), "lock")]
    cmd += list(extra)
    if user:
        cmd = ["runuser", "-u", user, "--"] + cmd
    p = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, **(env or {})})
    events = []
    for line in p.stdout.splitlines():
        try:
            events.append(json.loads(line.lstrip("<0123456789>")))
        except ValueError:
            pass
    return p.returncode, events, p.stderr, p.stdout


def check(name, cond, detail=""):
    results.append(cond)
    print(f"{'PASS' if cond else 'FAIL'}  {name}" + (f"   [{detail}]" if detail and not cond else ""))


def last(ev, kind):
    found = [e for e in ev if e["event"] == kind]
    return found[-1] if found else {}


def listing(servers):
    return sorted(os.listdir(servers))


def main():
    base = tempfile.mkdtemp(prefix="vscleanup-test-")
    os.chmod(base, 0o755)
    servers = os.path.join(base, ".vscode-server", "cli", "servers")
    os.makedirs(servers)
    outside = os.path.join(base, "outside-precious")
    os.makedirs(outside)
    open(os.path.join(outside, "keep.txt"), "w").write("precious")
    procs = []
    immutable = None
    try:
        # --- fixtures (Stable channel) -------------------------------------------------
        c_old = make(servers, "Stable", 1, "1.100.0", 40)             # old, unused -> delete
        c_old2 = make(servers, "Stable", 5, "1.120.0", 50)            # old, unused -> delete
        c_active = make(servers, "Stable", 2, "1.130.0", 30)          # old, but a process uses it -> keep
        c_third = make(servers, "Stable", 3, "1.141.0", 20)           # 2nd newest complete -> keep
        c_newest = make(servers, "Stable", 4, "1.142.0", 16)          # newest complete -> keep
        s_orphan = make(servers, "Stable", 11, "1.110.0", 10, staging=True)    # orphan -> delete
        s_young = make(servers, "Stable", 12, "1.143.0", 2, staging=True)      # young -> keep
        s_fd = make(servers, "Stable", 13, "1.111.0", 10, staging=True)        # fd held -> keep
        s_sibling = make(servers, "Stable", 2, "1.130.0", 10, staging=True)    # sibling of in-use final -> keep
        c_partial_unk = make(servers, "Stable", 21, None, 30, complete=False, with_pkg=False)  # unclear -> keep
        c_incomplete_old = make(servers, "Stable", 22, "1.101.0", 30, complete=False)          # incomplete+old -> delete
        c_incomplete_new = make(servers, "Stable", 23, "1.150.0", 20, complete=False)          # newer than newest complete -> keep
        s_of_new = make(servers, "Stable", 23, "1.150.0", 10, staging=True)                    # its staging -> delete
        # all markers present but far too few files (partially populated by the update race)
        c_hollow = make(servers, "Stable", 24, "1.145.0", 20, pad=0)
        # other channels
        ins = make(servers, "Insiders", 31, "1.200.0", 100)                                    # only complete in channel -> keep
        exp = make(servers, "Exploration", 41, "1.300.0", 100, complete=False)                 # no complete in channel -> keep
        # hostile / unrelated entries
        os.symlink(outside, os.path.join(servers, f"Stable-{h(99)}"))                          # symlink -> never touched
        os.makedirs(os.path.join(servers, "foo-bar"))
        open(os.path.join(servers, "lru.json"), "w").write("[]")

        procs.append(subprocess.Popen(["sleep", "600"], cwd=os.path.join(c_active, "server")))
        procs.append(subprocess.Popen(["sleep", "600"], stdin=open(os.path.join(s_fd, "server", "package.json"))))
        time.sleep(0.5)

        before = listing(servers)

        # --- dry-run: nothing may change ------------------------------------------------
        rc, ev, err, _ = run(servers)
        dec = {e["entry"]: e for e in ev if e["event"] == "decision"}
        check("dry-run exits 0", rc == 0, err)
        check("dry-run changes nothing", listing(servers) == before)
        want_delete = {os.path.basename(p) for p in (c_old, c_old2, c_incomplete_old, s_orphan, s_of_new)}
        got_delete = {n for n, e in dec.items() if e["action"] == "delete"}
        check("dry-run plans exactly the expected deletions", got_delete == want_delete, f"{sorted(got_delete)}")

        # --- apply ----------------------------------------------------------------------
        rc, ev, err, _ = run(servers, "--apply")
        left = set(listing(servers))
        check("apply exits 0", rc == 0, err)
        check("1: old unused install removed", os.path.basename(c_old) not in left and os.path.basename(c_old2) not in left)
        check("2: old but active install kept", os.path.basename(c_active) in left)
        check("3: newest and 2nd-newest complete kept", os.path.basename(c_newest) in left and os.path.basename(c_third) in left)
        check("4: orphaned staging removed", os.path.basename(s_orphan) not in left)
        check("5: staging held open by process kept", os.path.basename(s_fd) in left)
        check("5: young staging kept", os.path.basename(s_young) in left)
        check("5: staging sibling of in-use install kept", os.path.basename(s_sibling) in left)
        check("8: unclear version (partial, no package.json) kept", os.path.basename(c_partial_unk) in left)
        check("8: incomplete final newer than newest complete kept", os.path.basename(c_incomplete_new) in left)
        check("8: incomplete outdated final removed", os.path.basename(c_incomplete_old) not in left)
        hollow = dec[os.path.basename(c_hollow)]
        check("8: hollow install (markers ok, files missing) is not counted as complete",
              hollow["kind"] == "install-incomplete" and os.path.basename(c_hollow) in left
              and os.path.basename(c_third) in left, str(hollow))
        check("staging of that newer install removed (age > 7d)", os.path.basename(s_of_new) not in left)
        check("other channel keeps its only complete install", os.path.basename(ins) in left)
        check("channel without complete install: nothing deleted", os.path.basename(exp) in left)
        check("symlink entry not followed or removed", os.path.islink(os.path.join(servers, f"Stable-{h(99)}"))
              and os.path.exists(os.path.join(outside, "keep.txt")))
        check("unrelated names untouched", "foo-bar" in left and "lru.json" in left)
        summ = last(ev, "summary")
        check("summary reports freed space", summ.get("deleted") == len(want_delete) and (summ.get("freed_mb") or 0) > 0, str(summ))
        check("summary says result=ok", summ.get("result") == "ok", str(summ))

        # --- 6: repeat run is a no-op ---------------------------------------------------
        snapshot = listing(servers)
        rc, ev, err, _ = run(servers, "--apply")
        summ = last(ev, "summary")
        check("6: repeated run changes nothing", rc == 0 and listing(servers) == snapshot and summ.get("deleted") == 0, str(summ))

        # --- active-write protection (default 60 min grace, fixtures are fresh) --------------
        make(servers, "Stable", 61, "1.090.0", 60)
        rc, ev, err, _ = run(servers, "--apply", "--active-grace-minutes", "60")
        check("5: recently written entries are kept (ctime guard)",
              os.path.isdir(os.path.join(servers, f"Stable-{h(61)}")) and
              all(e["action"] == "keep" for e in ev if e["event"] == "decision"))
        rc, ev, err, _ = run(servers, "--apply")
        check("   ...and removed once the guard no longer applies", not os.path.exists(os.path.join(servers, f"Stable-{h(61)}")))

        # --- journal priorities (systemd sets JOURNAL_STREAM) ----------------------------------
        rc, ev, err, raw = run(servers, env={"JOURNAL_STREAM": "1:1"})
        check("journal: info lines carry <6>, summary of a clean run too",
              raw.splitlines()[0].startswith("<6>") and raw.splitlines()[-1].startswith("<6>"), raw[:80])

        # --- 7: parallel run is prevented -----------------------------------------------
        make(servers, "Stable", 62, "1.091.0", 60)
        lock = os.path.join(base, "lock")
        holder = subprocess.Popen(["flock", "-n", lock, "sleep", "20"], start_new_session=True)
        time.sleep(0.5)
        rc, ev, err, _ = run(servers, "--apply")
        check("7: parallel run exits 75 and deletes nothing",
              rc == 75 and os.path.isdir(os.path.join(servers, f"Stable-{h(62)}")), f"rc={rc}")
        os.killpg(holder.pid, 9)  # flock's child (sleep) holds the lock, too
        holder.wait()

        # --- failures must be loud: a deletion that fails is an error, never "ok" -------------
        if os.geteuid() == 0:
            victim = make(servers, "Stable", 63, "1.092.0", 60)
            immutable = os.path.join(victim, "server", "node_modules", "mod0.js")
            if subprocess.run(["chattr", "+i", immutable], capture_output=True).returncode == 0:
                rc, ev, err, raw = run(servers, "--apply", env={"JOURNAL_STREAM": "1:1"})
                fail = [e for e in ev if e["event"] == "delete-failed"]
                summ = last(ev, "summary")
                check("failed deletion -> exit 1, delete-failed error event, summary result=errors",
                      rc == 1 and len(fail) == 1 and fail[0]["level"] == "error" and summ.get("result") == "errors"
                      and summ.get("level") == "error", f"rc={rc} {summ}")
                check("failed deletion is logged with journal priority <3>",
                      any(line.startswith("<3>") and "delete-failed" in line for line in raw.splitlines()))
                subprocess.run(["chattr", "-i", immutable], check=True)
                immutable = None
            else:
                print("SKIP  failed-deletion test (chattr +i not supported here)")

        # --- 8: unreadable process table -> no deletion ----------------------------------
        if os.geteuid() == 0:
            make(servers, "Stable", 64, "1.093.0", 60)
            subprocess.run(["chown", "-R", "nobody:nogroup", base], check=True)
            rc, ev, err, _ = run(servers, "--apply", user="nobody", lock=os.path.join(base, "lock-nobody"))
            summ = last(ev, "summary")
            check("8: incomplete process scan -> exit 3, nothing deleted, result=scan-incomplete",
                  rc == 3 and os.path.isdir(os.path.join(servers, f"Stable-{h(64)}")) and summ.get("result") == "scan-incomplete",
                  f"rc={rc}")
            subprocess.run(["chown", "-R", "root:root", base], check=True)

        # --- safety refusals --------------------------------------------------------------
        for bad in (os.path.dirname(servers), "/tmp", base):
            rc, _, _, _ = run(bad)
            check(f"refuses unsafe servers dir {bad.replace(base, '<tmp>')}", rc == 2, f"rc={rc}")
        link = os.path.join(base, "linked")
        os.makedirs(os.path.join(link + "-real", ".vscode-server", "cli"))
        os.symlink(servers, os.path.join(link + "-real", ".vscode-server", "cli", "servers"))
        rc, _, _, _ = run(os.path.join(link + "-real", ".vscode-server", "cli", "servers"))
        check("refuses symlinked servers dir", rc == 2, f"rc={rc}")
    finally:
        if immutable:
            subprocess.run(["chattr", "-i", immutable])
        for p in procs:
            p.kill()
        shutil.rmtree(base, ignore_errors=True)
    failed = results.count(False)
    print(f"\n{results.count(True)} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
