# android-ai-tester

Let an AI agent (Claude Code) run **scripted uTest test cases** and **exploratory testing sessions** on Android apps installed on your own phone, with organized evidence and bug reports already drafted in uTest format.

```
Claude Code ──► mobile-mcp ──┐
     │                       ├──► adb ──► your Android phone (USB or Wi-Fi)
     └────────► tools/droid ─┘
     │
     └─ guard_device.py hook (blocks dangerous actions on a personal device)
```

- **mobile-mcp** gives the AI "eyes and hands": screenshots, the on-screen element tree, taps, swipes and typing.
- **tools/droid** handles evidence and device state: video, screenshots, logcat, crashes, About Device info, device prep/restore and simulations (rotation, dark mode, large font, low battery, permissions, process death).
- **Skills** teach the workflow:
  - `android-device` – base skill: how to drive the device safely and collect evidence.
  - `utest-android-test-case` – executes a scripted uTest test case step by step.
  - `android-exploratory` – runs a charter-based, time-boxed exploratory session (SBTM style).

> The AI never submits anything. You review the results and submit tests and bugs to uTest yourself.

## 1. Requirements

- Linux (or macOS) with `adb`, `python3` and `node`/`npx`.
  - mobile-mcp needs Node 20+. If your system Node is older, `.mcp.json` automatically runs it with Node 22 through `npx` without touching your system install.
- [Claude Code](https://claude.com/claude-code).
- Optional: `scrcpy` (`sudo apt install scrcpy`) to mirror the screen on your PC and record video **with audio**.

## 2. Prepare the phone (one time)

1. Settings > About phone > tap **Build number** 7 times to enable Developer options.
2. In Developer options, enable **USB debugging**. On Xiaomi/POCO devices also enable **USB debugging (Security settings)**, which is required for adb taps.
3. Connect via USB, unlock the phone and accept **"Allow USB debugging"** (check "Always allow from this computer").
4. Wireless (Android 11+): Developer options > **Wireless debugging** > Pair device with pairing code, then:
   ```bash
   adb pair <ip>:<pairing-port>     # enter the code shown on the phone
   adb connect <ip>:<port>
   ```
   Note: over Wi-Fi, turning off the phone's Wi-Fi during a test drops the connection.

## 3. Project setup

```bash
cd android-ai-tester
bash scripts/setup.sh        # checks tools, creates config/device.env, pre-downloads mobile-mcp, runs the doctor
nano config/device.env       # set TARGET_PACKAGES (and ANDROID_SERIAL if more than one device is connected)
adb shell pm list packages | grep -i <app-name>   # find the app's package name
tools/droid doctor           # should show ✓ for the device and the app
```

### Configuration files

| File | Purpose | In git? |
|---|---|---|
| `config/device.env` | Device serial, target packages, prep options (DND, mute, show touches) | No (copy from `device.env.example`) |
| `config/accounts.env` | Test account credentials provided by the uTest cycle | No (copy from `accounts.env.example`) |

`TARGET_PACKAGES` is important: the guard hook only allows clearing data, uninstalling or changing permissions for these packages. The AI is instructed not to read `accounts.env`; when a login is needed, it asks you to type the credentials on the device.

Open Claude Code **in the project folder** (`claude`) and approve the `mobile-mcp` MCP server when prompted. Run `/mcp` to check that it is connected.

## 4. Usage

The project instructions (`CLAUDE.md`) and skills are written in Brazilian Portuguese, so the agent replies in pt-BR by default. You can prompt in any language.

**Scripted test case (uTest):** paste the test case into the chat, or save it to `test-cases/<name>.md` (see `test-cases/EXEMPLO.md`):

```
Run the test case in test-cases/login-profile.md on the app com.example.app
```

**Exploratory session:**

```
Run a 45-minute exploratory session on the checkout of com.example.app, focusing on interruptions and input.
```

Each execution creates `runs/YYYY-MM-DD_<slug>/` containing:

- `README.md` – suggested status for each step and draft notes;
- `FINAL-REPORT.md` – every bug, ready to paste into uTest;
- `evidence/step-N-*/`, `evidence/bugs/BUG-N/`, `bug-reports/BUG-N.md`, `logs/`.

Exploratory charters are saved in `charters/`. Review the results, check them against the cycle's Known Issues and submit them to uTest.

### Templates

`templates/` holds the formats the agent fills in: `bug-report.md`, `run-readme.md`, `final-report.md`, `charter.md` and `session-notes.md`. Edit them to change the output format.

## 5. Keeping your personal phone safe

The hook `.claude/hooks/guard_device.py` runs before every shell command and mobile-mcp call:

- **Blocks:** reboot, root, remount, factory reset, deleting files from `/sdcard`, uninstalling/clearing/changing permissions of non-target apps, `settings put secure`, calls/SMS/e-mail, `adb backup`.
- **Asks first:** Wi-Fi/mobile data/airplane mode, installing APKs, changing language/system properties, uninstalling the target app itself, opening another app through MCP, copying photos/downloads off the phone.

Additional rules (in `CLAUDE.md`): the agent only operates the apps in `TARGET_PACKAGES`, never spends money or contacts third parties without asking, and checks every piece of evidence for personal data before saving it.

`tools/droid prep` turns on Do Not Disturb (no personal notifications in recordings), keeps the screen awake, shows touches and mutes media volume. `tools/droid restore` undoes all of it. If a session is interrupted, run `tools/droid restore` manually.

Tips: use a **test account** in the app whenever possible and, if your Android version supports it, a **secondary user profile / Private Space** to isolate the app under test from your personal data.

## 6. Known limitations

- `screenrecord` videos have no audio and are limited to 180 s each (record in parts or use `scrcpy --record`).
- `adb input text` cannot type accents or emoji; the agent uses mobile-mcp typing instead.
- Screens with `FLAG_SECURE` (passwords, banking, DRM) appear black in screenshots and videos.
- Flutter/WebView apps and games may expose a poor element tree; the agent falls back to screenshots + coordinates (slower).
- Without root there is no real network throttling; bad-network simulations depend on you switching networks.

## `tools/droid` quick reference

Uses only the Python standard library. Every change made to the device is recorded in `.droid/state.json` and can be undone with `droid restore`. Run `tools/droid --help` for details.

```
doctor | run new <slug> | prep | restore | info [--out DIR]
shot <png> | rec start <mp4> | rec stop | log start | log stop | crashes | note "txt" [--step DIR]
ui [--grep txt] | tap X Y | tap-el N | swipe X1 Y1 X2 Y2 | text "abc" | key BACK|HOME|APP_SWITCH
launch | stop | bg | kill-bg | clear | focus
set dark on|off | font 1.3|reset | battery 5|reset | rotate 0|1|auto | anim off|reset
perm grant|revoke android.permission.X
```

## Project structure

```
.claude/skills/        skills (android-device, utest-android-test-case, android-exploratory)
.claude/hooks/         personal-device guard (PreToolUse hook)
.claude/settings.json  MCP enablement, permission allow/deny lists, hook registration
.mcp.json              mobile-mcp server definition
config/                device.env / accounts.env (not in git) and their .example files
scripts/setup.sh       one-time setup
tools/droid            helper CLI (Python + adb)
templates/             bug report, run README, final report, charter, session notes
test-cases/            pasted uTest test cases (not in git, except the example)
charters/              exploratory session charters (not in git)
runs/YYYY-MM-DD_slug/  one folder per execution (not in git)
```
