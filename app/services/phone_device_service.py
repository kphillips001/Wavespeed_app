import subprocess
from pathlib import Path


DEFAULT_PHONE_DEVICE_ID = "RFCN90JL1LP"
DEFAULT_SCRCPY_WINDOW_TITLE = "Ava"
DEFAULT_SCRCPY_DIR = Path(r"C:\scrcpy")
DEFAULT_SCRCPY_EXE = DEFAULT_SCRCPY_DIR / "scrcpy.exe"


class PhoneDeviceError(RuntimeError):
    pass


def wake_or_sleep_phone(device_id=DEFAULT_PHONE_DEVICE_ID):
    try:
        subprocess.run(
            [
                "adb",
                "-s",
                device_id,
                "shell",
                "input",
                "keyevent",
                "26",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise PhoneDeviceError("adb was not found on this PC.") from exc
    except subprocess.CalledProcessError as exc:
        error_text = (exc.stderr or exc.stdout or "").strip()
        raise PhoneDeviceError(
            error_text or "adb could not wake or sleep the phone."
        ) from exc


def launch_scrcpy(
    device_id=DEFAULT_PHONE_DEVICE_ID,
    window_title=DEFAULT_SCRCPY_WINDOW_TITLE,
):
    scrcpy_command = (
        str(DEFAULT_SCRCPY_EXE)
        if DEFAULT_SCRCPY_EXE.exists()
        else "scrcpy"
    )

    command = [
        scrcpy_command,
        "-s",
        device_id,
        "--audio-source=playback",
        "--window-title",
        window_title,
        "--stay-awake",
        "--always-on-top",
    ]

    try:
        return subprocess.Popen(
            command,
            cwd=str(DEFAULT_SCRCPY_DIR)
            if DEFAULT_SCRCPY_DIR.exists()
            else None,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    except FileNotFoundError as exc:
        raise PhoneDeviceError("scrcpy was not found on this PC.") from exc


def launch_phone_device(device_id=DEFAULT_PHONE_DEVICE_ID):
    wake_or_sleep_phone(device_id=device_id)
    return launch_scrcpy(device_id=device_id)


def is_process_running(pid):
    if not pid:
        return False

    result = subprocess.run(
        [
            "tasklist",
            "/FI",
            f"PID eq {pid}",
            "/FO",
            "CSV",
            "/NH",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    return str(pid) in result.stdout


def terminate_process(pid):
    if not pid:
        return False

    result = subprocess.run(
        [
            "taskkill",
            "/PID",
            str(pid),
            "/T",
            "/F",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    return result.returncode == 0


def terminate_scrcpy_fallback():
    result = subprocess.run(
        [
            "taskkill",
            "/IM",
            "scrcpy.exe",
            "/F",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    return result.returncode == 0


def close_phone_device(pid=None, device_id=DEFAULT_PHONE_DEVICE_ID):
    terminated = terminate_process(pid)

    if not terminated:
        terminate_scrcpy_fallback()

    wake_or_sleep_phone(device_id=device_id)
