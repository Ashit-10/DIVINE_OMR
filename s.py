import subprocess

process = subprocess.Popen(
    ["python", "autoapp.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

stdout, stderr = process.communicate()

if stdout:
    print("Output from autoapp.py:")
    print(stdout)

if stderr:
    print("Errors from autoapp.py:", file=sys.stderr)
    print(stderr, file=sys.stderr)
