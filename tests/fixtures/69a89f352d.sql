-- digest: 69a89f352d
-- macos: 27.0.1 (26A434)
-- database: system
CREATE TABLE admin (key TEXT PRIMARY KEY NOT NULL, value INTEGER NOT NULL);
CREATE TABLE policies (    id        INTEGER    NOT NULL PRIMARY KEY,     bundle_id    TEXT    NOT NULL,     uuid        TEXT    NOT NULL,     display        TEXT    NOT NULL,     UNIQUE (bundle_id, uuid));
CREATE TABLE active_policy (    client        TEXT    NOT NULL,     client_type    INTEGER    NOT NULL,     policy_id    INTEGER NOT NULL,     PRIMARY KEY (client, client_type),     FOREIGN KEY (policy_id) REFERENCES policies(id) ON DELETE CASCADE ON UPDATE CASCADE);
CREATE TABLE access (    service        TEXT        NOT NULL,     client         TEXT        NOT NULL,     client_type    INTEGER     NOT NULL,     auth_value     INTEGER     NOT NULL,     auth_reason    INTEGER     NOT NULL,     auth_version   INTEGER     NOT NULL,     csreq          BLOB,     policy_id      INTEGER,     indirect_object_identifier_type    INTEGER,     indirect_object_identifier         TEXT NOT NULL DEFAULT 'UNUSED',     indirect_object_code_identity      BLOB,     flags          INTEGER,     last_modified  INTEGER     NOT NULL DEFAULT (CAST(strftime('%s','now') AS INTEGER)),     pid            INTEGER,     pid_version    INTEGER,     boot_uuid      TEXT NOT NULL DEFAULT 'UNUSED',     last_reminded  INTEGER     NOT NULL DEFAULT (CAST(strftime('%s','now') AS INTEGER)), one_time_reprompt_eligible INTEGER, reminder_count INTEGER NOT NULL DEFAULT 0,     PRIMARY KEY (service, client, client_type, indirect_object_identifier),    FOREIGN KEY (policy_id) REFERENCES policies(id) ON DELETE CASCADE ON UPDATE CASCADE);
CREATE TABLE access_overrides (    service        TEXT    NOT NULL PRIMARY KEY);
CREATE TABLE expired (    service        TEXT        NOT NULL,     client         TEXT        NOT NULL,     client_type    INTEGER     NOT NULL,     csreq          BLOB,     last_modified  INTEGER     NOT NULL ,     expired_at     INTEGER     NOT NULL DEFAULT (CAST(strftime('%s','now') AS INTEGER)),     PRIMARY KEY (service, client, client_type));
CREATE TABLE integrity_flag (    key TEXT PRIMARY KEY NOT NULL,    value INTEGER NOT NULL);
CREATE TABLE managed_overrides (    service        TEXT        NOT NULL,     client         TEXT        NOT NULL,     client_type    INTEGER     NOT NULL,     auth_value     INTEGER     NOT NULL DEFAULT 1,     auth_reason    INTEGER     NOT NULL,     auth_version   INTEGER     NOT NULL,     csreq          BLOB,     policy_id      INTEGER,     indirect_object_identifier_type    INTEGER,     indirect_object_identifier         TEXT NOT NULL DEFAULT 'UNUSED',     indirect_object_code_identity      BLOB,     flags          INTEGER     NOT NULL DEFAULT 0,     last_modified  INTEGER     NOT NULL DEFAULT (CAST(strftime('%s','now') AS INTEGER)),     one_time_reprompt_eligible INTEGER,     admin_auth_value    INTEGER NOT NULL,    PRIMARY KEY (service, client, client_type, indirect_object_identifier),     FOREIGN KEY (policy_id) REFERENCES policies(id) ON DELETE CASCADE ON UPDATE CASCADE);
CREATE INDEX active_policy_id ON active_policy(policy_id);
CREATE INDEX idx_managed_overrides_service ON managed_overrides(service);
CREATE INDEX idx_managed_overrides_client ON managed_overrides(client);
CREATE INDEX idx_managed_overrides_client_type ON managed_overrides(client_type);
CREATE INDEX idx_managed_overrides_auth_value ON managed_overrides(auth_value);
CREATE INDEX idx_managed_overrides_flags ON managed_overrides(flags);
CREATE INDEX idx_managed_overrides_admin_auth_value ON managed_overrides(admin_auth_value);
CREATE INDEX idx_managed_overrides_csreq ON managed_overrides(csreq);
