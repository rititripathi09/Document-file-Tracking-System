CREATE TABLE IF NOT EXISTS departments (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY, name TEXT, email TEXT, phone TEXT, notes TEXT, file TEXT, department INTEGER NULL REFERENCES departments(id) ON DELETE SET NULL ON UPDATE CASCADE);
CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, file INTEGER REFERENCES files(id) ON DELETE CASCADE ON UPDATE CASCADE, type TEXT, previous INTEGER NULL REFERENCES departments(id), updated INTEGER NULL REFERENCES departments(id), time INTEGER DEFAULT CURRENT_TIMESTAMP);

INSERT OR IGNORE INTO departments (id, name) VALUES (1, "Administration"), (2, "Store"), (3, "Workshop-1"), (4, "Workshop-2");
INSERT OR IGNORE INTO files VALUES(1,'Public','public@user.email','9876543210','URGENT','JBT-WHT-FONT170X.jpeg',NULL);
CREATE TRIGGER IF NOT EXISTS file_CHANGED AFTER UPDATE OF department ON files BEGIN INSERT INTO logs(file, type, previous, updated) VALUES (old.id, 'Department', old.department, new.department); END