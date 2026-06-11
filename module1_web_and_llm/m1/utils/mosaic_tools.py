"""
Helper functions for building, starting, and checking the MOSAIC search engine.

MOSAIC: https://mosaic.ows.eu
Source: https://opencode.it4i.eu/openwebsearcheu-public/mosaic
"""

import glob
import os
import pathlib
import platform
import re
import subprocess
import time
from IPython.display import display, HTML
import requests
import urllib

MOSAIC_REPO_URL = "https://opencode.it4i.eu/openwebsearcheu-public/mosaic.git"
MOSAIC_PORT = 8008


def _java_version_at(java_home: str):
    """
    Run `<java_home>/bin/java -version` and return the major version as an int,
    or None if it can't be determined.

    Handles both old-style ("1.8.0_471" -> 8) and new-style ("17.0.9" -> 17,
    "26.0.1" -> 26) version strings.
    """
    java_bin = os.path.join(java_home, "bin", "java")
    if not os.path.exists(java_bin):
        return None

    result = subprocess.run([java_bin, "-version"], capture_output=True, text=True)
    output = result.stdout + result.stderr
    m = re.search(r'version "(\d+)(?:\.(\d+))?', output)
    if not m:
        return None

    major = int(m.group(1))
    if major == 1 and m.group(2):  # old-style "1.8.x" -> Java 8
        return int(m.group(2))
    return major


def find_java17plus_home(min_version: int = 17):
    """
    Locate an installed JDK with version >= min_version.

    Returns the JDK home path as a string, or None if not found.
    """
    system = platform.system()
    candidates = []

    if system == "Darwin":  # macOS
        # 1. Ask java_home for an exact match (with --failfast so it doesn't
        #    silently fall back to a default/legacy JVM)
        result = subprocess.run(
            ["/usr/libexec/java_home", "-v", f"{min_version}+", "--failfast"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            candidates.append(result.stdout.strip())

        # 2. Also scan common install locations (Homebrew JDKs often aren't
        #    registered with java_home unless symlinked)
        candidates += sorted(
            glob.glob("/Library/Java/JavaVirtualMachines/*/Contents/Home")
        )
        candidates += sorted(
            glob.glob(
                "/opt/homebrew/Cellar/openjdk*/*/libexec/openjdk.jdk/Contents/Home"
            )
        )
        candidates += sorted(
            glob.glob("/opt/homebrew/opt/openjdk*/libexec/openjdk.jdk/Contents/Home")
        )
        candidates += sorted(
            glob.glob("/usr/local/Cellar/openjdk*/*/libexec/openjdk.jdk/Contents/Home")
        )
        candidates += sorted(
            glob.glob("/usr/local/opt/openjdk*/libexec/openjdk.jdk/Contents/Home")
        )

    elif system == "Linux":
        candidates += sorted(glob.glob("/usr/lib/jvm/*")) + sorted(
            glob.glob("/opt/java/*")
        )

    elif system == "Windows":
        candidates += sorted(
            glob.glob(r"C:\Program Files\Eclipse Adoptium\jdk-*")
        ) + sorted(glob.glob(r"C:\Program Files\Java\jdk-*"))

    # Pick the candidate with the highest actual Java version >= min_version
    best_path, best_version = None, 0
    for c in candidates:
        if not os.path.isdir(c):
            continue
        version = _java_version_at(c)
        if version is not None and version >= min_version and version > best_version:
            best_path, best_version = c, version

    return best_path


def setup_java_env(min_version: int = 17) -> bool:
    """
    Find a JDK with version >= min_version and set JAVA_HOME / PATH
    in the current process's environment so subprocess calls (mvn, java)
    pick it up.

    Returns True if a suitable JDK was found and configured, False otherwise.
    """
    java_home = find_java17plus_home(min_version=min_version)

    if java_home is None:
        print(
            f"⚠️  Could not auto-detect Java {min_version}+. Please set JAVA_HOME manually, e.g.:"
        )
        print(f'   os.environ["JAVA_HOME"] = "/path/to/jdk-{min_version}"')
        return False

    os.environ["JAVA_HOME"] = java_home
    sep = ";" if platform.system() == "Windows" else ":"
    extra_paths = [os.path.join(java_home, "bin")]

    # On macOS, also make sure common Homebrew bin dirs (where mvn/git often
    # live) are on PATH — Jupyter kernels launched via Finder/Spotlight don't
    # always inherit a shell's full PATH.
    if platform.system() == "Darwin":
        for p in ("/opt/homebrew/bin", "/opt/homebrew/sbin", "/usr/local/bin"):
            if os.path.isdir(p) and p not in os.environ["PATH"]:
                extra_paths.append(p)

    os.environ["PATH"] = sep.join(extra_paths) + sep + os.environ["PATH"]
    print("Using Java:", java_home)
    return True


def build_mosaic(mosaic_dir: str = "mosaic") -> bool:
    """
    Clone (if needed) and build MOSAIC from source.

    Parameters
    ----------
    mosaic_dir : str
        Path where the MOSAIC repo is/will be located.

    Returns
    -------
    bool
        True if the build succeeded, False otherwise.
    """
    mosaic_path = pathlib.Path(mosaic_dir).resolve()

    print("cwd:        ", pathlib.Path.cwd())
    print("mosaic_dir: ", mosaic_path, "exists:", mosaic_path.exists())

    # 1. Clone if not already present
    if not mosaic_path.exists():
        print(f"Cloning MOSAIC into {mosaic_path.resolve()} ...")
        result = subprocess.run(
            ["git", "clone", MOSAIC_REPO_URL, str(mosaic_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("❌ git clone failed:")
            print(result.stderr)
            return False
        print("✅ Cloned MOSAIC")
    else:
        print(f"MOSAIC already present at {mosaic_path.resolve()}, skipping clone.")

    # 2. Run the build script
    scripts_dir = mosaic_path / "scripts"
    build_script = "build.sh" if platform.system() != "Windows" else "build.bat"
    build_script_path = scripts_dir / build_script

    if not build_script_path.exists():
        print(f"❌ Build script not found: {build_script_path}")
        return False

    print(f"Running {build_script} (this can take a few minutes)...")
    result = subprocess.run(
        [str(build_script_path)],
        cwd=str(scripts_dir),
        capture_output=True,
        text=True,
    )

    print(result.stdout[-2000:])  # show tail of output
    if result.returncode != 0:
        print("❌ Build failed:")
        print(result.stderr[-2000:])
        return False

    print("✅ MOSAIC built successfully")
    return True


def start_mosaic(mosaic_dir: str = "mosaic", wait_seconds: int = 10):
    """
    Start the MOSAIC service in the background so the notebook stays responsive.

    Parameters
    ----------
    mosaic_dir : str
        Path to the MOSAIC repo (must already be built — see build_mosaic()).
    wait_seconds : int
        How long to wait after launching before reporting status.

    Returns
    -------
    subprocess.Popen
        The running MOSAIC process handle.
    """
    mosaic_path = pathlib.Path(mosaic_dir).resolve()
    scripts_dir = mosaic_path / "scripts"
    start_script = "start.sh" if platform.system() != "Windows" else "start.bat"
    start_script_path = scripts_dir / start_script

    print("cwd:             ", pathlib.Path.cwd())
    print("mosaic_dir:      ", mosaic_path, "exists:", mosaic_path.exists())
    print("scripts_dir:     ", scripts_dir, "exists:", scripts_dir.exists())
    print("start_script:    ", start_script_path, "exists:", start_script_path.exists())

    if not mosaic_path.exists():
        print(f"❌ MOSAIC directory not found: {mosaic_path}")
        print("   Did you clone it (build_mosaic()) in this same working directory?")
        return None

    if not start_script_path.exists():
        print(f"❌ Start script not found: {start_script_path}")
        print("   Did you run build_mosaic() first?")
        return None

    process = subprocess.Popen(
        [str(start_script_path)],
        cwd=str(scripts_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    print(f"MOSAIC starting (PID {process.pid}) — waiting {wait_seconds} seconds...")
    time.sleep(wait_seconds)

    if process.poll() is not None:
        print("⚠️  MOSAIC exited early! Output:")
        print(process.stdout.read())
    else:
        print(
            f"✅ MOSAIC still running. Try http://localhost:{MOSAIC_PORT}/search?q=graz"
        )

    return process


def check_java() -> bool:
    """Check that Java is installed and print its version."""
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True)
    except FileNotFoundError:
        print("❌ Java not found — please install Java 17 (Temurin recommended).")
        return False

    line = (result.stdout or result.stderr or "not found").splitlines()[0]
    print("Java:", line)
    if result.returncode == 0:
        print("✅ Java found")
        return True
    print("❌ Java not found.")
    return False


def check_maven() -> bool:
    """Check that Maven is installed and print its version."""
    try:
        result = subprocess.run(["mvn", "--version"], capture_output=True, text=True)
    except FileNotFoundError:
        print("❌ Maven not found — 'mvn' is not installed or not on your PATH.")
        return False

    line = (result.stdout or result.stderr or "not found").splitlines()[0]
    print("Maven:", line)
    if result.returncode == 0:
        print("✅ Maven found")
        return True
    print("❌ Maven not found.")
    return False


def query_mosaic(q, top: int = 10, index_name: str = "waw_os", base_url: str = "http://localhost:8008/search"):
    params = {"q": q, "index": index_name, "limit": top}
    # url =    f"https://qnode.eu/ows/mosaic/service/search?q={query}?&index=demo-simplewiki&language=eng&limit=5"

    # Encode the parameters
    encoded_params = urllib.parse.urlencode(params)

    # Construct the full URL
    full_url = f"{base_url}?{encoded_params}"
    query_result = ""
    try:
        response = requests.get(full_url, params=params)
        response.raise_for_status()
        query_result = response.json()
        # print(json.dumps(json_response, indent=4))
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

    return query_result


def _dedup(results: list) -> list:
    """Deduplicate by URL, keep highest score, return top-n."""
    seen, deduped = set(), []
    for r in results:
        if r["url"] not in seen:
            seen.add(r["url"])
            deduped.append(r)
    return deduped


def retrieve(
    queries, top: int = 10, base_url: str = "http://localhost:8008/search", index_name: str = "waw_os"
) -> list:
    """
    Retrieve from the local MOSAIC index.
    queries : single query string or list of query strings
    n       : number of top results to return
    """
    if isinstance(queries, str):
        queries = [queries]
    all_results = []
    for q in queries:
        try:
            hits = query_mosaic(q, top=top, index_name = index_name, base_url=base_url)

            for hit in hits["results"]:
                for item in hit[index_name]:
                    all_results.append(
                        {
                            "id": item.get("id", 0),
                            "text": item.get("textSnippet", ""),
                            "url": item.get("url", ""),
                            "title": item.get("title", ""),
                        }
                    )
        except Exception as e:
            print(f"⚠️  MOSAIC query '{q}' failed: {e}")
    return _dedup(all_results)


def display_results(results: list, title: str = "Results"):
    """Render retrieval results as neat HTML cards in the notebook."""
    html = f"<h3>{title} &nbsp;<small style='color:#888'>({len(results)} hits)</small></h3>"
    for i, r in enumerate(results, 1):
        snippet = (r.get("text", "") or "")[:250].replace("<", "&lt;")
        html += f"""
        <div style='border:1px solid #ddd;border-radius:6px;padding:12px;margin:8px 0;
                    font-family:sans-serif;font-size:13px'>
          <b>#{i}</b> &nbsp;
          <span style='background:#e8f4fd;border-radius:4px;padding:2px 6px;font-size:11px'>
            {r.get('url','')}</span> &nbsp;
          <a href='{r.get('url','')}' target='_blank' style='color:#1a73e8'>
            {r.get('title','(no title)')[:90]}</a><br/>
          <span style='color:#555'>{snippet}…</span>
        </div>"""
    display(HTML(html))
