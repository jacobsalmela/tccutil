"""Run tccutil.py against TCC.db schemas harvested from real Macs.

Each tests/fixtures/<digest>.sql is replayed into a temporary database, and
tccutil.py runs against it as if on the macOS version the fixture came from.
Nothing touches the real TCC.db, so this runs on any OS with Python 3 and the
`packaging` module:

    python3 -m unittest discover -s tests -v
"""

import contextlib
import glob
import hashlib
import importlib
import io
import os
import re
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES = os.path.join(ROOT, 'tests', 'fixtures')
sys.path.insert(0, ROOT)


def load_fixture(path):
    """Parse a fixture's `-- key: value` header and keep its SQL."""
    with open(path) as f:
        sql = f.read()
    meta = dict(re.findall(r'^-- (\w+): (.*)$', sql, re.MULTILINE))
    return {
        'path': path,
        'name': os.path.splitext(os.path.basename(path))[0],
        'digest': meta.get('digest'),
        'macos': meta.get('macos', '').split()[0],
        'sql': sql,
    }


FIXTURE_LIST = [load_fixture(p) for p in sorted(glob.glob(os.path.join(FIXTURES, '*.sql')))]


def supported_digests():
    """The access table digests tccutil.py accepts."""
    with open(os.path.join(ROOT, 'tccutil.py')) as f:
        return set(re.findall(r'"([0-9a-f]{10})"', f.read()))


def access_digest(db):
    """Compute the access table digest the same way tccutil.py does."""
    conn = sqlite3.connect(db)
    try:
        sql = conn.execute("SELECT sql FROM sqlite_master WHERE name='access' and type='table'").fetchone()[0]
    finally:
        conn.close()
    return hashlib.sha1(sql.encode('utf-8')).hexdigest()[0:10]


def run_tccutil(db, macos, *args):
    """Run tccutil.py's main() against db as if on macOS `macos`.

    tccutil.py reads the macOS version at import time, so it is re-imported for
    every run with platform.mac_ver patched. Returns (exit code, stdout, stderr).
    """
    argv = ['tccutil.py', *args]
    stdout, stderr = io.StringIO(), io.StringIO()
    with mock.patch('platform.mac_ver', return_value=(macos, ('', '', ''), '')), \
            mock.patch.object(sys, 'argv', argv):
        sys.modules.pop('tccutil', None)
        tccutil = importlib.import_module('tccutil')
        tccutil.tcc_db = db
        tccutil.sudo = True
        code = 0
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                tccutil.main()
            except SystemExit as e:
                code = e.code
    return code, stdout.getvalue(), stderr.getvalue()


class SchemaTests:
    """Tests run against every fixture; subclasses set `fixture`."""

    fixture = None

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.tmp.name, 'TCC.db')
        conn = sqlite3.connect(self.db)
        conn.executescript(self.fixture['sql'])
        conn.close()

    def tearDown(self):
        self.tmp.cleanup()

    def tccutil(self, *args):
        return run_tccutil(self.db, self.fixture['macos'], *args)

    def rows(self, client, service='kTCCServiceAccessibility'):
        conn = sqlite3.connect(self.db)
        conn.row_factory = sqlite3.Row
        try:
            return [dict(r) for r in conn.execute(
                "SELECT * FROM access WHERE client=? AND service=?", (client, service))]
        finally:
            conn.close()

    def enabled_value(self, row):
        return row['auth_value'] if 'auth_value' in row else row['allowed']

    def test_fixture_matches_its_digest(self):
        self.assertEqual(self.fixture['digest'], self.fixture['name'],
                         'fixture file name must be its digest')
        self.assertEqual(access_digest(self.db), self.fixture['digest'],
                         'replayed schema does not produce the digest in the header')

    def test_digest_is_supported(self):
        self.assertIn(self.fixture['digest'], supported_digests())

    def test_digest_flag(self):
        code, out, err = self.tccutil('--digest')
        self.assertEqual(code, 0, err)
        self.assertEqual(out.strip(), self.fixture['digest'])

    def test_insert_bundle_id(self):
        code, _, err = self.tccutil('-i', 'com.example.app')
        self.assertEqual(code, 0, err)
        self.assertEqual(err, '')
        rows = self.rows('com.example.app')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['client_type'], 0)
        self.assertNotEqual(self.enabled_value(rows[0]), 0)

    def test_insert_path(self):
        code, _, err = self.tccutil('-i', '/usr/bin/osascript')
        self.assertEqual(code, 0, err)
        self.assertEqual(err, '')
        rows = self.rows('/usr/bin/osascript')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['client_type'], 1)

    def test_insert_twice_keeps_one_row(self):
        self.tccutil('-i', 'com.example.app')
        code, _, err = self.tccutil('-i', 'com.example.app')
        self.assertEqual(code, 0, err)
        self.assertEqual(len(self.rows('com.example.app')), 1)

    def test_insert_other_service(self):
        code, _, err = self.tccutil('-s', 'kTCCServiceScreenCapture', '-i', 'com.example.app')
        self.assertEqual(code, 0, err)
        self.assertEqual(len(self.rows('com.example.app', 'kTCCServiceScreenCapture')), 1)
        self.assertEqual(self.rows('com.example.app'), [])

    def test_list(self):
        self.tccutil('-i', 'com.example.one', '-i', '/usr/bin/osascript')
        self.tccutil('-s', 'kTCCServiceScreenCapture', '-i', 'com.example.other')
        code, out, err = self.tccutil('--list')
        self.assertEqual(code, 0, err)
        self.assertEqual(sorted(out.split()), ['/usr/bin/osascript', 'com.example.one'])

    def test_disable_then_enable(self):
        self.tccutil('-i', 'com.example.app')
        code, _, err = self.tccutil('-d', 'com.example.app')
        self.assertEqual(code, 0, err)
        self.assertEqual(self.enabled_value(self.rows('com.example.app')[0]), 0)
        code, _, err = self.tccutil('-e', 'com.example.app')
        self.assertEqual(code, 0, err)
        self.assertNotEqual(self.enabled_value(self.rows('com.example.app')[0]), 0)

    def test_remove(self):
        self.tccutil('-i', 'com.example.app', '-i', '/usr/bin/osascript')
        code, _, err = self.tccutil('-r', 'com.example.app', '-r', '/usr/bin/osascript')
        self.assertEqual(code, 0, err)
        self.assertEqual(self.rows('com.example.app'), [])
        self.assertEqual(self.rows('/usr/bin/osascript'), [])

    def assert_write_fails(self, event, *args):
        """Make `event` on the access table fail, then expect tccutil to report it and exit 1."""
        # A trigger leaves the access table's CREATE statement, and so its digest, unchanged.
        conn = sqlite3.connect(self.db)
        conn.execute(f"CREATE TRIGGER fail_{event.lower()} BEFORE {event} ON access "
                     "BEGIN SELECT RAISE(ABORT, 'simulated failure'); END")
        conn.commit()
        conn.close()
        code, _, err = self.tccutil(*args)
        self.assertEqual(code, 1, err)
        self.assertIn('simulated failure', err)
        self.assertNotIn('SIP', err)

    def test_failed_insert_exits_with_error(self):
        self.assert_write_fails('INSERT', '-i', 'com.example.app')

    def test_failed_disable_exits_with_error(self):
        self.tccutil('-i', 'com.example.app')
        self.assert_write_fails('UPDATE', '-d', 'com.example.app')

    def test_failed_enable_exits_with_error(self):
        self.tccutil('-i', 'com.example.app')
        self.assert_write_fails('UPDATE', '-e', 'com.example.app')

    def test_failed_remove_exits_with_error(self):
        self.tccutil('-i', 'com.example.app')
        self.assert_write_fails('DELETE', '-r', 'com.example.app')

    def test_readonly_database_suggests_sip(self):
        if os.geteuid() == 0:
            self.skipTest('root can write to read-only files')
        os.chmod(self.db, 0o444)
        code, _, err = self.tccutil('-i', 'com.example.app')
        self.assertEqual(code, 1, err)
        self.assertIn('readonly database', err)
        self.assertIn('SIP', err)


# One test class per fixture, named after its digest (e.g. TestSchema_f773496775).
for _fixture in FIXTURE_LIST:
    _name = f"TestSchema_{_fixture['name']}"
    globals()[_name] = type(_name, (SchemaTests, unittest.TestCase), {'fixture': _fixture})


class CoverageTests(unittest.TestCase):

    def test_every_supported_digest_has_a_fixture(self):
        missing = sorted(supported_digests() - {f['digest'] for f in FIXTURE_LIST})
        if missing:
            self.skipTest(f"no fixture yet for: {', '.join(missing)}")

    def test_unknown_schema_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, 'TCC.db')
            conn = sqlite3.connect(db)
            conn.execute("CREATE TABLE access (service TEXT, client TEXT)")
            conn.close()
            code, _, err = run_tccutil(db, '26.0', '--list')
        self.assertEqual(code, 1)
        self.assertIn('TCC Database structure is unknown', err)


if __name__ == '__main__':
    unittest.main()
