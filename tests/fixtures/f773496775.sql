-- digest: f773496775
-- macos: 26.6.2 (25G83)
-- database: user
CREATE TABLE admin (key TEXT PRIMARY KEY NOT NULL, value INTEGER NOT NULL);
CREATE TABLE policies (	id		INTEGER	NOT NULL PRIMARY KEY, 	bundle_id	TEXT	NOT NULL, 	uuid		TEXT	NOT NULL, 	display		TEXT	NOT NULL, 	UNIQUE (bundle_id, uuid));
CREATE TABLE active_policy (	client		TEXT	NOT NULL, 	client_type	INTEGER	NOT NULL, 	policy_id	INTEGER NOT NULL, 	PRIMARY KEY (client, client_type), 	FOREIGN KEY (policy_id) REFERENCES policies(id) ON DELETE CASCADE ON UPDATE CASCADE);
CREATE TABLE access_overrides (	service		TEXT	NOT NULL PRIMARY KEY);
CREATE TABLE expired (    service        TEXT        NOT NULL,     client         TEXT        NOT NULL,     client_type    INTEGER     NOT NULL,     csreq          BLOB,     last_modified  INTEGER     NOT NULL ,     expired_at     INTEGER     NOT NULL DEFAULT (CAST(strftime('%s','now') AS INTEGER)),     PRIMARY KEY (service, client, client_type));
CREATE TABLE "access" (    service        TEXT        NOT NULL,     client         TEXT        NOT NULL,     client_type    INTEGER     NOT NULL,     auth_value     INTEGER     NOT NULL,     auth_reason    INTEGER     NOT NULL,     auth_version   INTEGER     NOT NULL,     csreq          BLOB,     policy_id      INTEGER,     indirect_object_identifier_type    INTEGER,     indirect_object_identifier         TEXT NOT NULL DEFAULT 'UNUSED',     indirect_object_code_identity      BLOB,     flags          INTEGER,     last_modified  INTEGER     NOT NULL DEFAULT (CAST(strftime('%s','now') AS INTEGER)), pid INTEGER, pid_version INTEGER, boot_uuid TEXT NOT NULL DEFAULT 'UNUSED', last_reminded INTEGER NOT NULL DEFAULT 0,     PRIMARY KEY (service, client, client_type, indirect_object_identifier),    FOREIGN KEY (policy_id) REFERENCES policies(id) ON DELETE CASCADE ON UPDATE CASCADE);
CREATE TABLE integrity_flag (    key TEXT PRIMARY KEY NOT NULL,    value INTEGER NOT NULL);
CREATE INDEX active_policy_id ON active_policy(policy_id);
