"""External runtime setup: Deno (JS runtime for yt-dlp) and yt-dlp defaults."""

import shutil

from src.constants import HOME
from src.shell import print_h, run


def install_deno():
    print_h("Installing Deno (JS runtime for yt-dlp)")

    # If already installed, skip
    if shutil.which("deno"):
        run(["deno", "--version"], check=False)
        print("✅ Deno already installed.")
        return

    # Install Deno to ~/.deno/bin/deno
    # Use bash -lc so ~ expands correctly and we can use pipes
    run('curl -fsSL https://deno.land/x/install/install.sh | sh', check=False)

    deno_bin = HOME / ".deno" / "bin"
    deno_exe = deno_bin / "deno"

    if deno_exe.exists():
        print(f"✅ Deno installed at {deno_exe}")
        run([str(deno_exe), "--version"], check=False)
    else:
        print("⚠️ Deno install script ran but deno binary not found at ~/.deno/bin/deno")

    # Ensure PATH for future login shells (helpful, but not sufficient for autostart)
    profile = HOME / ".profile"
    export_line = 'export PATH="$HOME/.deno/bin:$PATH"'
    try:
        profile.touch(exist_ok=True)
        text = profile.read_text(encoding="utf-8")
        if ".deno/bin" not in text:
            profile.write_text(text.rstrip() + "\n" + export_line + "\n", encoding="utf-8")
            print(f"✅ Added Deno PATH to {profile}")
    except Exception as e:
        print(f"⚠️ Could not update {profile}: {e}")


def install_ytdlp_config():
    print_h("Configuring yt-dlp defaults")
    cfg_dir = HOME / ".config" / "yt-dlp"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    cfg_file = cfg_dir / "config"
    cfg_file.write_text(
        "--js-runtimes deno\n"
        "-t mp4\n"
        "--merge-output-format mp4\n",
        encoding="utf-8",
    )
    print(f"✅ Wrote {cfg_file}")
