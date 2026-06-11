import subprocess
import shutil
import urllib.request


def diagnose_owilix():
    """Check each possible failure point for owilix remote search and print a report."""

    print("=" * 55)
    print("OWILIX DIAGNOSTICS")
    print("=" * 55)

    # 1. Is owilix on PATH?
    owilix_path = shutil.which("owilix")
    if owilix_path:
        print(f"\n✅ owilix found at: {owilix_path}")
    else:
        print("\n❌ owilix not on PATH.")
        print("   Fix: run the install instructions (Section 1) in your terminal,")
        print("   then restart Jupyter from the same terminal.")
        return  # no point continuing

    # 2. Does owilix respond at all?
    r = subprocess.run(["owilix", "--version"], capture_output=True, text=True, timeout=5)
    if r.returncode == 0:
        print(f"✅ owilix version: {r.stdout.strip()}")
    else:
        print(f"❌ owilix --version failed: {r.stderr.strip()}")

    # 3. Can owilix reach the remote index?
    print("\nChecking remote connection (owilix remote doctor)...")
    r = subprocess.run(["owilix", "remote", "doctor"],
                       capture_output=True, text=True, timeout=15)
    output = (r.stdout + r.stderr).strip()
    print(output if output else "(no output)")
    if r.returncode != 0:
        print("❌ Remote doctor failed — the remote index may be unreachable.")

    # 4. Basic internet connectivity
    print("\nChecking internet connectivity...")
    try:
        urllib.request.urlopen("https://openwebindex.net", timeout=5)
        print("✅ openwebindex.net is reachable")
    except Exception as e:
        print(f"❌ Cannot reach openwebindex.net: {e}")
        print("   Check your network / VPN / firewall.")

    # 5. Minimal search with full raw output
    print("\nTrying minimal search (no --fetch, no --select, limit 1)...")
    r = subprocess.run(
        ["owilix", "remote", "search", "test", "--limit", "1"],
        capture_output=True, text=True, timeout=20
    )
    print("STDOUT:", r.stdout[:500] or "(empty)")
    print("STDERR:", r.stderr[:500] or "(empty)")
    print("Return code:", r.returncode)

    print("\n" + "=" * 55)
