"""Behavior checks for reversible appearance updates and safe remote launching."""
import argparse
import json
from pathlib import Path
import runpy
import shlex
import tempfile
import unittest
from unittest.mock import patch
import subprocess
import os
import pty
import select
import sys
import time

W = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'tools/ghostty-workbench'))


class AppearanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = W['Store'](self.tmp.name)

    def test_install_preserves_original_and_is_idempotent(self):
        original = '# personal\nconfig-file = retro/atari\nscrollback-limit = 104857600'
        self.store.config.write_text(original)
        self.store.install()
        first = self.store.config.read_text()
        self.store.install()
        self.assertEqual(first, self.store.config.read_text())
        self.assertEqual(original, self.store.config.with_name('config.before-workbench').read_text())
        self.assertLess(first.index('retro/atari'), first.index('workbench-appearance.conf'))
        self.assertIn('scrollback-limit = 104857600', first)

    def test_cancel_and_crash_restore_exact_bytes(self):
        for original in (None, '# old\nfont-size = 17\n'):
            if original is None:
                self.store.managed.unlink(missing_ok=True)
            else:
                self.store.managed.write_text(original)
            self.store.begin()
            self.store.write_preview('foreground = #112233\n')
            # A fresh Store instance is the next invocation after a crash.
            fresh = W['Store'](self.tmp.name)
            self.assertTrue(fresh.restore())
            self.assertEqual(original, W['text_or_none'](fresh.managed))
            self.assertFalse(fresh.journal.exists())

    def test_commit_keeps_choice_and_removes_journal(self):
        self.store.begin()
        self.store.write_preview('font-size = 18\n')
        self.store.commit({'font': 'Monaco'})
        self.assertFalse(self.store.restore())
        self.assertEqual('font-size = 18\n', self.store.managed.read_text())
        self.assertEqual('Monaco', json.loads(self.store.selection.read_text())['font'])

    def test_external_edits_are_not_clobbered(self):
        self.store.begin()
        self.store.write_preview('font-size = 18\n')
        self.store.managed.write_text('# edited by user\n')
        with self.assertRaises(W['WorkbenchError']):
            self.store.restore()
        self.assertEqual('# edited by user\n', self.store.managed.read_text())
        self.assertTrue(self.store.journal.exists())

    def test_write_ahead_recovery_handles_crash_before_replace(self):
        self.store.managed.write_text('old')
        self.store.begin()
        self.store.write_preview('preview-one')
        data = json.loads(self.store.journal.read_text())
        data.update(previous='preview-one', expected='preview-two')
        self.store.journal.write_text(json.dumps(data))
        self.store.restore()
        self.assertEqual('old', self.store.managed.read_text())

    def test_lock_rejects_second_writer(self):
        with self.store.lock():
            with self.assertRaises(W['WorkbenchError']):
                with W['Store'](self.tmp.name).lock():
                    pass

    def test_font_and_shader_overrides_clear_inherited_lists(self):
        profile = Path(self.tmp.name) / 'profile'
        profile.write_text('font-family = "Retro Mono"\ncustom-shader = /old/crt.glsl\nforeground = #abcdef\ncommand = evil\n')
        item = {'kind': 'retro', 'path': str(profile)}
        text = W['render'](item, 'Other Mono', 16, 'off', [('foreground', '#ffffff')])
        self.assertIn('font-family = ""', text)
        self.assertIn('font-family-bold = ""', text)
        self.assertNotIn('Retro Mono', text)
        self.assertIn('font-family = "Other Mono"', text)
        self.assertNotIn('/old/crt.glsl', text)
        self.assertNotIn('command = evil', text)
        self.assertIn('custom-shader =\n', text)

    def test_color_theme_cannot_execute_commands_or_override_font(self):
        theme = Path(self.tmp.name) / 'theme'
        theme.write_text('foreground = #abcdef\nfont-family = Bad\nconfig-file = evil\ncommand = evil\n')
        text = W['render']({'kind': 'theme', 'path': str(theme)}, None, None, 'auto', [('font-family', 'Monaco')])
        self.assertNotIn('evil', text)
        self.assertNotIn('Bad', text)
        self.assertIn('font-family = Monaco', text)

    def test_symlinked_config_is_updated_without_breaking_link(self):
        real = Path(self.tmp.name) / 'real-config'
        real.write_text('scrollback-limit = 999\n')
        self.store.config.symlink_to(real)
        self.store.install()
        self.assertTrue(self.store.config.is_symlink())
        self.assertIn('scrollback-limit = 999', real.read_text())

    def test_sparse_retro_fonts_are_resolved_before_declaring_fallback(self):
        calls = []

        def fake_run(argv):
            calls.append(argv)
            if '--family=Sparse Mono' in argv:
                return 'Sparse Mono\n  SparseMono-Regular\n'
            if '--family=Missing' in argv:
                return ''
            return 'Monaco\n  Monaco\n'

        with patch.dict(W['fonts'].__globals__, run=fake_run, ghostty=lambda: 'ghostty'):
            names = W['fonts'](['Sparse Mono', 'Missing', 'Monaco', None, ''])
        self.assertEqual(['Monaco', 'Sparse Mono'], names)
        self.assertEqual(3, len(calls))


class RemoteTests(unittest.TestCase):
    def args(self, **values):
        return argparse.Namespace(**dict(host='server', port=None, identity=None,
            socket=None, session=None, **values))

    def test_remote_names_are_data_and_attachment_uses_stable_id(self):
        output = '$1\t2\t0\twork; $(touch bad) "quotes"\n$2\t1\t1\tother\n'
        with patch('subprocess.run', return_value=subprocess.CompletedProcess([], 0, output, '')):
            sessions = W['tmux_discover'](self.args())
        self.assertEqual(2, len(sessions))
        argv = shlex.split(sessions[0]['command'])
        self.assertEqual(['tmux', 'attach-session', '-t', '$1'], shlex.split(argv[-1].split('fi; exec ', 1)[1]))
        self.assertNotIn('touch bad', sessions[0]['command'])
        self.assertIn('work; $(touch bad)', W['tmux_script'](sessions))

    def test_remote_terminal_fallback_and_supported_terminal(self):
        with patch('subprocess.run', return_value=subprocess.CompletedProcess([], 0, '$1\t1\t0\twork\n', '')):
            remote = shlex.split(W['tmux_discover'](self.args())[0]['command'])[-1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, body in [('infocmp', 'exit "$INFO_STATUS"'),
                               ('tmux', 'printf "%s\\n" "$TERM" "$@"')]:
                path = root / name
                path.write_text('#!/bin/sh\n' + body + '\n')
                path.chmod(0o755)
            for status, expected in [('0', 'xterm-ghostty'), ('1', 'xterm-256color')]:
                result = subprocess.run(['/bin/sh', '-c', remote], capture_output=True, text=True,
                    env={**os.environ, 'PATH': directory, 'TERM': 'xterm-ghostty', 'INFO_STATUS': status})
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual([expected, 'attach-session', '-t', '$1'], result.stdout.splitlines())
                self.assertEqual(status == '1', 'remote terminfo unavailable' in result.stderr)

    def test_invalid_host_never_reaches_ssh(self):
        args = self.args()
        args.host = '-oProxyCommand=evil'
        with patch('subprocess.run') as spawn:
            with self.assertRaises(W['WorkbenchError']):
                W['tmux_discover'](args)
            spawn.assert_not_called()

    def test_no_server_is_empty_but_auth_failure_is_an_error(self):
        with patch('subprocess.run', return_value=subprocess.CompletedProcess([], 1, '', 'no server running on /tmp/tmux')):
            self.assertEqual([], W['tmux_discover'](self.args()))
        with patch('subprocess.run', return_value=subprocess.CompletedProcess([], 255, '', 'Permission denied')):
            with self.assertRaises(W['WorkbenchError']):
                W['tmux_discover'](self.args())

    def test_malformed_discovery_fails_before_launch(self):
        with patch('subprocess.run', return_value=subprocess.CompletedProcess([], 0, 'welcome shell banner\n', '')):
            with self.assertRaises(W['WorkbenchError']):
                W['tmux_discover'](self.args())

    def test_missing_session_is_explicit(self):
        args = self.args()
        args.session = ['missing']
        with patch('subprocess.run', return_value=subprocess.CompletedProcess([], 0, '$1\t1\t0\twork\n', '')):
            with self.assertRaises(W['WorkbenchError']):
                W['tmux_discover'](args)


class PickerTerminalTests(unittest.TestCase):
    def test_real_curses_navigation_cancel_and_save(self):
        # A real PTY exercises curses input/output; native reload is a separate
        # macOS smoke check. This test never touches the user's app or config.
        script = Path(__file__).resolve().parents[1] / 'tools/ghostty-workbench'
        for ending in (b'q', b'\r'):
            with self.subTest(ending=ending), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                state = root / 'ghostty'
                state.mkdir()
                original = '# original\nfont-size = 17\n'
                managed = state / 'workbench-appearance.conf'
                managed.write_text(original)
                for name, color in [('one', '#112233'), ('two', '#445566')]:
                    (root / name).write_text(f'foreground = {color}\nfont-family = Monaco\n')
                helper = root / 'child.py'
                helper.write_text(f'''
import runpy, argparse, json
from pathlib import Path
w = runpy.run_path({str(script)!r})
s = w['Store']({str(state)!r})
s.begin()
w['picker'].__globals__.update(reload_config=lambda: None,
    validate_config=lambda s: None, ghostty=lambda: 'ghostty',
    run=lambda *a, **k: 'font-family = Monaco\\nforeground = #ffffff\\n')
a = argparse.Namespace(start=None, kind='all', fonts=False)
items = [dict(id='retro:'+n, name=n, kind='retro', path=str(Path({str(root)!r})/n))
         for n in ['one', 'two']]
try:
    result = w['picker'](s, items, ['Monaco', 'Menlo'], a,
        [('font-family', 'Monaco'), ('foreground', '#ffffff')])
    if result:
        s.commit(result)
finally:
    s.restore()
''')
                master, slave = pty.openpty()
                proc = subprocess.Popen([sys.executable, str(helper)], stdin=slave,
                    stdout=slave, stderr=slave, env=dict(os.environ, TERM='xterm-256color'))
                os.close(slave)
                output = bytearray()

                def wait_for(predicate):
                    deadline = time.monotonic() + 5
                    while time.monotonic() < deadline:
                        if select.select([master], [], [], .05)[0]:
                            try:
                                output.extend(os.read(master, 65536))
                            except OSError:
                                pass
                        if predicate():
                            return
                    self.fail(bytes(output[-2000:]).decode(errors='replace'))

                try:
                    wait_for(lambda: b'Ghostty workbench' in output)
                    os.write(master, b'j')
                    wait_for(lambda: '#445566' in managed.read_text())
                    os.write(master, b'\tj')
                    wait_for(lambda: 'font-family = "Menlo"' in managed.read_text())
                    os.write(master, b'c')
                    wait_for(lambda: 'custom-shader-animation = true' in managed.read_text())
                    os.write(master, ending)
                    wait_for(lambda: proc.poll() is not None)
                    self.assertEqual(0, proc.returncode, bytes(output[-2000:]))
                    self.assertFalse((state / '.workbench-preview.json').exists())
                    if ending == b'q':
                        self.assertEqual(original, managed.read_text())
                    else:
                        choice = json.loads((state / '.workbench-selection.json').read_text())
                        self.assertEqual('retro:two', choice['id'])
                        self.assertEqual('Menlo', choice['font'])
                        self.assertEqual('on', choice['crt'])
                finally:
                    if proc.poll() is None:
                        proc.kill()
                        proc.wait()
                    os.close(master)


class CRTTests(unittest.TestCase):
    def test_tuner_save_and_cancel_preserve_other_settings(self):
        for save in (True, False):
            with self.subTest(save=save), tempfile.TemporaryDirectory() as folder:
                store = W['Store'](folder)
                store.install()
                original = 'font-family = Monaco\nforeground = #abcdef\n'
                store.managed.write_text(original)
                with patch.dict(os.environ, TERM_PROGRAM='ghostty', SSH_CONNECTION=''), \
                     patch.object(sys.stdin, 'isatty', return_value=True), \
                     patch.dict(W['tune_crt'].__globals__, validate_config=lambda s: None,
                                reload_config=lambda: None), \
                     patch('curses.wrapper', return_value=save):
                    self.assertEqual(0, W['tune_crt'](store, argparse.Namespace(dry_run=False)))
                shader = Path(folder) / 'shaders/crt.glsl'
                self.assertEqual(save, shader.exists())
                self.assertIn(original.strip(), store.managed.read_text())
                self.assertFalse(store.journal.exists())
                if not save:
                    self.assertEqual(original, store.managed.read_text())

    def test_shader_roundtrip_and_reject_unknown_format(self):
        source = (Path(__file__).resolve().parents[1] / 'shaders/crt.glsl').read_text()
        values = W['shader_values'](source)
        values['BLOOM'] = .2
        updated = W['shader_with_values'](source, values)
        self.assertEqual(.2, W['shader_values'](updated)['BLOOM'])
        self.assertIn('void mainImage', updated)
        with self.assertRaises(W['WorkbenchError']):
            W['shader_values'](source.replace('CURVATURE', 'UNKNOWN'))

    def test_shader_override_preserves_palette_font_and_is_idempotent(self):
        original = '# personal\nfont-family = Monaco\nforeground = #abcdef\ncustom-shader = old\n'
        updated = W['crt_config'](original, Path('/tmp/crt.glsl'))
        self.assertIn('font-family = Monaco\nforeground = #abcdef', updated)
        self.assertNotIn('= old', updated)
        self.assertEqual(updated, W['crt_config'](updated, Path('/tmp/crt.glsl')))

    def test_shader_and_appearance_recover_together(self):
        with tempfile.TemporaryDirectory() as folder:
            store = W['Store'](folder)
            shader = Path(folder) / 'shaders/crt.glsl'
            W['atomic'](shader, 'original shader')
            W['atomic'](store.managed, 'font-size = 17\n')
            store.begin(files=[shader])
            store.write_resource(shader, 'preview shader')
            store.write_preview('font-size = 18\n')
            self.assertTrue(W['Store'](folder).restore())
            self.assertEqual('original shader', shader.read_text())
            self.assertEqual('font-size = 17\n', store.managed.read_text())

    def test_external_shader_edit_blocks_restore_and_commit(self):
        with tempfile.TemporaryDirectory() as folder:
            store = W['Store'](folder)
            shader = Path(folder) / 'crt.glsl'
            store.begin(files=[shader])
            store.write_resource(shader, 'preview')
            shader.write_text('external edit')
            with self.assertRaises(W['WorkbenchError']):
                store.commit({})
            with self.assertRaises(W['WorkbenchError']):
                store.restore()
            self.assertEqual('external edit', shader.read_text())
            self.assertTrue(store.journal.exists())


if __name__ == '__main__':
    unittest.main()
