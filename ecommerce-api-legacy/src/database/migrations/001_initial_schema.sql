CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    pass TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    price REAL NOT NULL,
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY,
    enrollment_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY,
    action TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_enrollments_user_id ON enrollments(user_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_payments_enrollment_id ON payments(enrollment_id);
