#!/usr/bin/env python3
"""Run one heavy command under the host's shared admission policy.

    python3 tools/run.py -- cargo build --release
    python3 tools/run.py --cad -- tools/cad-venv/bin/python native_part.py
    python3 tools/run.py -- bazel build //:funnel-cover
    python3 tools/run.py --timing -- tools/cad-venv/bin/python part.py
    python3 tools/run.py --count 1

Children share the verified lease. New logical roots obey the host count,
concurrent-start stagger and pressure policy; timing reserves every slot.
The Bazel wrapper uses one action at a time; Cargo compiles with two jobs.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
import _run_slots as slots


def script_key(command):
    program = Path(command[0]).name
    if program in ('bazel', 'bazelisk'):
        verb = next((a for a in command[1:] if not a.startswith('-')), 'build')
        targets = sorted(a for a in command[1:] if a.startswith(('//', '@')))
        return 'bazel:' + verb + ':' + ','.join(targets)
    for arg in command:
        if arg.endswith(('.py', '.js', '.mjs', '.sh', '.ts', '.tsx')):
            path = Path(arg)
            try:
                return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
            except ValueError:
                return path.name
    if program in ('cargo', 'rustc'):
        chosen = []
        for flag in ('--manifest-path', '--bin', '-p', '--package'):
            if flag in command and command.index(flag) + 1 < len(command):
                value = command[command.index(flag) + 1]
                if flag == '--manifest-path':
                    try:
                        value = str(Path(value).resolve().relative_to(Path.cwd().resolve()))
                    except ValueError:
                        value = Path(value).name
                chosen += [flag, value]
        return program + ':' + ':'.join(chosen)
    return program


def limit_jobs(command, jobs):
    """Keep process-level children within this logical run's declared parallelism."""
    before, after = (command[:command.index('--')], command[command.index('--'):]) if '--' in command else (command, [])
    kept, skip = [], False
    for arg in before:
        if skip:
            skip = False
        elif arg in ('--jobs', '-j'):
            skip = True
        elif not arg.startswith('--jobs=') and not (arg.startswith('-j') and arg[2:].isdigit()):
            kept.append(arg)
    return [*kept, f'--jobs={jobs}', *after]


def workspace_root():
    here = Path.cwd().resolve()
    for root in (here, *here.parents):
        if any((root / name).exists() for name in ('.bazelversion', 'MODULE.bazel', 'WORKSPACE', 'WORKSPACE.bazel')):
            return root
    return here


def viewer_producer(command, root):
    """A local viewer and the outputs of one outer hardware Python producer, when known."""
    if os.environ.get('HSM_VIEWER_PRODUCER') or not Path(command[0]).name.startswith('python'):
        return None
    script = next((Path(arg).resolve() for arg in command[1:] if arg.endswith('.py')), None)
    if script is None or not script.is_relative_to(root / 'hardware'):
        return None
    import socket
    candidates = [('127.0.0.1', 3000), ('127.0.0.1', 3001)]
    if url := os.environ.get('HSM_VIEWER_URL'):
        from urllib.parse import urlsplit
        parsed = urlsplit(url)
        if parsed.scheme != 'http' or parsed.hostname not in ('localhost', '127.0.0.1', '::1'):
            return None
        candidates = [(parsed.hostname, parsed.port or 80)]
    for host, port in candidates:
        try:
            with socket.create_connection((host, port), timeout=0.05) as sock:
                import http.client
                from contextlib import closing
                with closing(http.client.HTTPConnection(host, port, timeout=0.05)) as connection:
                    connection.sock = sock
                    connection.request('GET', '/api/hsm')
                    response = connection.getresponse()
                    data = json.loads(response.read()) if response.status == 200 else {}
            if isinstance(data, dict) and data.get('root') == str(root) and isinstance(data.get('notify'), str):
                graph = root / 'tools/bazel/graph.json'
                try:
                    writes = json.loads(graph.read_text())[script.relative_to(root).as_posix()]['writes']
                    outputs = [root / name for name in writes]
                except (OSError, ValueError, KeyError):
                    outputs = []
                return (host, port, data['notify'], root, script.parent, outputs)
        except (OSError, ValueError):
            pass                                # no local viewer; no output scan or extra work
    return None


def viewer_snapshot(producer):
    """Only the declared outputs and the producer's own directory, including new files."""
    if producer is None:
        return {}
    _host, _port, _token, root, directory, outputs = producer
    paths = set(outputs) | set(directory.iterdir())
    found = {}
    for path in paths:
        if path.name.startswith('.') or not path.is_relative_to(root / 'hardware'):
            continue
        if not path.name.endswith(('.step', '.step.mesh', '.glb', '.dxf', '.pdf', '.mmd')):
            continue
        try:
            st = path.stat()
            found[path] = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)
        except OSError:
            pass
    return found


def viewer_completed(producer, before):
    if producer is None:
        return
    host, port, token, root, _directory, _outputs = producer
    files = set()
    for path, stamp in viewer_snapshot(producer).items():
        if before.get(path) != stamp:
            name = path.relative_to(root / 'hardware').as_posix()
            files.add(name.removesuffix('.mesh') if name.endswith('.step.mesh') else name)
    if files:
        import http.client
        from contextlib import closing
        try:
            with closing(http.client.HTTPConnection(host, port, timeout=0.1)) as connection:
                connection.request('POST', '/api/hsm/files-changed',
                                   json.dumps({'root': str(root), 'files': sorted(files)}),
                                   {'Content-Type': 'application/json', 'X-HSM-Notify': token})
                connection.getresponse().read()
        except OSError:
            pass                                # polling remains the fallback


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--count', type=int)
    parser.add_argument('--timing', action='store_true')
    parser.add_argument('--cad', action='store_true')
    parser.add_argument('--check-inherited', action='store_true')
    parser.add_argument('--key')
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.count is not None:
        slots.set_count(args.count)
        print(f'{slots.directory() / "count"}: {args.count}')
        return 0
    if args.check_inherited:
        return 0 if slots.current() else 1
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('name a command after --')
    key = args.key or script_key(command)
    try:
        producer = viewer_producer(command, workspace_root())
        before = viewer_snapshot(producer)
    except Exception:
        producer, before = None, {}             # optional notification never holds a command
    stable = None
    guard = None
    program = Path(command[0]).name
    bazel_heavy = program in ('bazel', 'bazelisk') and any(v in command[1:] for v in ('build', 'test', 'run', 'coverage'))
    cargo_heavy = program == 'cargo' and any(v in command[1:] for v in ('build', 'test', 'run', 'check', 'bench', 'install', 'rustc'))
    if bazel_heavy:
        command = limit_jobs(command, 1)     # one heavy action per inherited logical lease
    elif cargo_heavy:
        command = limit_jobs(command, 2)
    if program in ('bazel', 'bazelisk'):
        stable = slots.broker_config(workspace_root())
        path = Path(json.loads(stable)['path'])
        guard = os.open(path.with_suffix('.guard'), os.O_RDWR | os.O_CREAT, 0o600)
        fcntl.flock(guard, fcntl.LOCK_EX)       # before booking any global capacity
    if args.cad or bazel_heavy:
        from _run_lock import wait_legacy
        wait_legacy()                         # older CAD parents may still need a kernel child
    try:
        slots.acquire(key, timing=args.timing)
    except slots.TimingLeaseError as error:
        print(f'[run] {error}', file=sys.stderr)
        return 2
    if args.cad or bazel_heavy:
        from _run_lock import acquire
        acquire(key, root=workspace_root())
    if bazel_heavy or cargo_heavy:
        slots.acquire_compiler()
    broker = slots.Broker(stable)
    slots._broker = broker
    env = slots.child_env()
    env['CARGO_BUILD_JOBS'] = '2'
    if Path(command[0]).name.startswith('python'):
        env['HSM_VIEWER_PRODUCER'] = '1'          # nested helpers cannot announce the outer run
    descriptors = slots.pass_fds()
    if program in ('bazel', 'bazelisk'):
        # A persistent JVM must not retain this caller's lease. Actions use the broker.
        descriptors = ()
        for name in (slots.RUN_ENV, slots.CAD_ENV, slots.COMPILER_ENV, 'HSM_RUN_PROFILE', 'HSM_NO_BUILD_LOCK'):
            env.pop(name, None)
    began = time.perf_counter()
    try:
        child = subprocess.Popen(command, env=env, pass_fds=descriptors)
        _pid, status, usage = os.wait4(child.pid, 0)
        child.returncode = os.waitstatus_to_exitcode(status)
        if args.timing:
            peak = int(usage.ru_maxrss * (1 if sys.platform == 'darwin' else 1024))
            print(json.dumps({'command_seconds': time.perf_counter() - began,
                              'peak_process_rss_bytes': peak}), file=sys.stderr)
    finally:
        broker.close()
        slots._broker = None
        if guard is not None:
            os.close(guard)
    if child.returncode == 0:
        try:
            viewer_completed(producer, before)
        except Exception:
            pass                                # polling remains the fallback
    return child.returncode if child.returncode >= 0 else 128 - child.returncode



if __name__ == '__main__':
    sys.exit(main())
