# TCC.db schema fixtures

Each `<digest>.sql` file is the schema of a real `TCC.db`, copied exactly as SQLite stores it. `tccutil.py` recognizes a database by the first 10 hex characters of the SHA-1 of the `access` table's stored `CREATE TABLE` text, so a fixture is only useful if that text is byte-for-byte identical to a real one. The tests replay each fixture into a temporary database and fail if it doesn't reproduce the digest in its file name.

Fixtures contain only the schema, never any rows.

## Adding a fixture

On the Mac, give your terminal Full Disk Access, then from the repository root:

```bash
tests/fixtures/harvest.sh user > /tmp/tcc.sql
sudo tests/fixtures/harvest.sh system > /tmp/tcc-system.sql
```

The first line of each file is `-- digest: <digest>`. Save it as `tests/fixtures/<digest>.sql`. If you already have that digest, you don't need to save it again.

## Running the tests

Needs Python 3 and `packaging`. Runs on any OS; the real `TCC.db` is never touched.

```bash
python3 -m unittest discover -s tests -v
```

A skipped `test_every_supported_digest_has_a_fixture` lists the digests `tccutil.py` accepts that don't have a fixture yet.
