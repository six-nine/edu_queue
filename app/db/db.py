import psycopg2
import psycopg2.pool
import typing as tp

from app.models.models import *

class Database:
    def __init__(self, *, dbname: str, user: str, password: str, host: str, port: int, debug: bool = False):
        self.__connection_pool = psycopg2.pool.ThreadedConnectionPool(1, -1,
                                                       dbname=dbname,
                                                       user=user,
                                                       password=password,
                                                       host=host,
                                                       port=port)
        if debug:
            self.__debug_clear()
        self.__init_tables()

    def __init_tables(self) -> None:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS users (
                               id BIGINT PRIMARY KEY,
                               name TEXT NOT NULL
                           );
                           CREATE TABLE IF NOT EXISTS groups (
                               id TEXT PRIMARY KEY,
                               owner_id BIGINT NOT NULL REFERENCES users(id),
                               name TEXT NOT NULL
                           );
                           CREATE INDEX IF NOT EXISTS groups_owner_id ON groups(owner_id);
                           CREATE TABLE IF NOT EXISTS groups_students (
                               group_id TEXT NOT NULL REFERENCES groups(id),
                               student_id BIGINT NOT NULL REFERENCES users(id),
                               PRIMARY KEY (group_id, student_id)
                           );
                           CREATE INDEX IF NOT EXISTS groups_students_student_id ON groups_students(student_id);
                           CREATE TABLE IF NOT EXISTS labs (
                               id TEXT PRIMARY KEY,
                               group_id TEXT NOT NULL REFERENCES groups(id),
                               name TEXT NOT NULL,
                               deadline TIMESTAMPTZ NOT NULL
                           );
                           CREATE INDEX IF NOT EXISTS labs_group_id ON labs(group_id);
                           CREATE TABLE IF NOT EXISTS labs_results (
                               lab_id TEXT REFERENCES labs(id),
                               student_id BIGINT NOT NULL REFERENCES users(id),
                               attempts_count SMALLINT NOT NULL DEFAULT 0,
                               is_passed BOOLEAN NOT NULL DEFAULT FALSE,
                               PRIMARY KEY (lab_id, student_id)
                           );
                           CREATE INDEX IF NOT EXISTS labs_results_student_id ON labs_results(student_id);
                           CREATE TABLE IF NOT EXISTS comparators(
                               id TEXT PRIMARY KEY,
                               owner_id BIGINT,
                               name TEXT NOT NULL,
                               data SMALLINT[] NOT NULL
                           );
                           CREATE INDEX IF NOT EXISTS comparators_owner_id ON comparators(owner_id);
                           CREATE TABLE IF NOT EXISTS queues (
                               id TEXT PRIMARY KEY,
                               group_id TEXT NOT NULL REFERENCES groups(id),
                               name TEXT NOT NULL,
                               date TIMESTAMPTZ NOT NULL,
                               comparator_id TEXT NOT NULL REFERENCES comparators(id)
                           );
                           CREATE INDEX IF NOT EXISTS queues_group_id ON queues(group_id);
                           CREATE TABLE IF NOT EXISTS queues_subscribers (
                               queue_id TEXT NOT NULL REFERENCES queues(id),
                               student_id BIGINT NOT NULL REFERENCES users(id),
                               lab_id TEXT NOT NULL REFERENCES labs(id),
                               PRIMARY KEY (queue_id, student_id)
                           );
                           CREATE INDEX IF NOT EXISTS queues_subscribers_group_id ON queues_subscribers(student_id);

                           INSERT INTO comparators(id, owner_id, name, data) VALUES
                           ('random_comparator', NULL, 'Random', %s)
                           ON CONFLICT(id) DO NOTHING;
                           ''', ("{" + "}",))
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)

    def __debug_clear(self) -> None:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''
                           DROP TABLE IF EXISTS users CASCADE;
                           DROP TABLE IF EXISTS groups CASCADE;
                           DROP TABLE IF EXISTS groups_students CASCADE;
                           DROP TABLE IF EXISTS labs CASCADE;
                           DROP TABLE IF EXISTS labs_results CASCADE;
                           DROP TABLE IF EXISTS queues CASCADE;
                           DROP TABLE IF EXISTS queues_subscribers CASCADE;
                           DROP TABLE IF EXISTS comparators CASCADE;
                           DROP TABLE IF EXISTS system_comparators CASCADE;
                           ''')
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)

    def create_user(self, *, user_id: int, name: str) -> None:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''
                           INSERT INTO users(id, name) VALUES
                           (%s, %s)
                           ON CONFLICT(id) DO UPDATE
                           SET name = EXCLUDED.name
                           ''', (user_id, name))
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)

    def create_group(self, *, group: Group) -> str:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            query = '''
                    INSERT INTO groups(id, owner_id, name) VALUES
                    (%s, %s, %s);
                    '''
            if len(group.labs) > 0:
                query += '''INSERT INTO labs(id, group_id, name, deadline) VALUES'''
                for i in range(len(group.labs)):
                    lab = group.labs[i]
                    if i != 0:
                        query += ', '
                    query += "('" + lab.id + "', '" + group.id + "', '" + lab.name + "', '" + lab.deadline.astimezone().isoformat() + "')"
                query += ';'
            cursor.execute(query, (group.id, group.owner_id, group.name))
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)
        return group.id

    def add_new_lab_to_group(self, *, lab: Lab, group_id: str) -> None:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''
                           INSERT INTO labs(id, group_id, name, deadline) VALUES
                           (%s, %s, %s, %s)''', (lab.id, group_id, lab.name, lab.deadline.astimezone().isoformat()))
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)

    def get_lab(self, *, lab_id: str) -> Lab:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''
                           SELECT id, group_id, name, deadline
                           FROM labs
                           WHERE id = %s''', (lab_id, ))
            rows = cursor.fetchall()
            assert len(rows) == 1
            row = rows[0]
            result = Lab(id=row[0], group_id=row[1], name=row[2], deadline=row[3])
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)
        return result

    def join_group(self, *, group_id: str, student_id: int) -> bool:
        result = True
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            try:
                cursor.execute('''INSERT INTO groups_students(group_id, student_id) VALUES (%s, %s)''', (group_id, student_id))
            except psycopg2.errors.ForeignKeyViolation:
                result = False
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)
        return result

    def quit_group(self, *, group_id: str, student_id: int) -> bool:
        result = True
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''DELETE FROM groups_students WHERE group_id = %s AND student_id = %s''', (group_id, student_id))
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)
        return result

    def get_student_groups(self, *, student_id: int) -> tp.List[BriefGroup]:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''
                           SELECT id, name
                           FROM groups
                           JOIN groups_students
                           ON groups.id = groups_students.group_id
                           WHERE groups_students.student_id = %s''', (student_id, ))
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append(BriefGroup(id=row[0], name=row[1]))
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)
        return result

    def get_group_students(self, *, group_id: str) -> tp.List[int]:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''
                           SELECT student_id
                           FROM groups_students
                           WHERE group_id = %s''', (group_id, ))
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append(row[0])
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)
        return result

    def get_teacher_groups(self, *, teacher_id: int) -> tp.List[BriefGroup]:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''
                           SELECT id, name
                           FROM groups
                           WHERE owner_id = %s''', (teacher_id, ))
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append(BriefGroup(id=row[0], name=row[1]))
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)
        return result

    def create_queue(self, *, queue: Queue) -> None:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''INSERT INTO queues(id, group_id, name, date, comparator_id) VALUES (%s, %s, %s, %s, %s)''', (queue.id, queue.group_id, queue.name, queue.date.astimezone().isoformat(), queue.comparator_id))
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)

    def delete_queue(self, *, queue_id: str) -> None:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''
                           DELETE FROM queues_subscribers WHERE queue_id = %s;
                           DELETE FROM queues WHERE id = %s;
                           ''', (queue_id, queue_id))
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)
        pass

    def get_queue(self, *, queue_id: str) -> Queue:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''
                           SELECT id, group_id, name, date, comparator_id
                           FROM queues
                           WHERE id = %s''', (queue_id, ))
            rows = cursor.fetchall()
            assert len(rows) == 1
            row = rows[0]
            result = Queue(id=row[0], group_id=row[1], name=row[2], date=row[3], comparator_id=row[4])
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)
        return result

    def get_group_queues(self, *, group_id: str) -> tp.List[BriefQueue]:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''
                           SELECT id, name, date
                           FROM queues
                           WHERE group_id = %s''', (group_id, ))
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append(BriefQueue(id=row[0], name=row[1], date=row[2]))
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)
        return result

    def get_student_queues(self, *, student_id: int) -> tp.List[BriefQueue]:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''
                           SELECT id, name, date
                           FROM queues
                           JOIN groups_students
                           ON groups_students.group_id = queues.group_id
                           WHERE groups_students.student_id = %s''', (student_id, ))
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append(BriefQueue(id=row[0], name=row[1], date=row[2]))
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)
        return result

    def get_teacher_queues(self, *, teacher_id: int) -> tp.List[BriefQueue]:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''
                           SELECT queues.id, queues.name, queues.date
                           FROM queues
                           JOIN groups
                           ON groups.id = queues.group_id
                           WHERE groups.owner_id = %s''', (teacher_id, ))
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append(BriefQueue(id=row[0], name=row[1], date=row[2]))
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)
        return result

    def get_queue_students(self, *, queue_id: str) -> tp.List[QueueStudent]:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''
                           SELECT student_id, lab_id
                           FROM queues_subscribers
                           WHERE queue_id = %s
                           ''', (queue_id, ))
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append(QueueStudent(student_id=row[0], lab_id=row[1]))
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)
        return result

    def sign_in_queue(self, *, queue_id: str, student_id: int, lab_id: str) -> None:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''INSERT INTO queues_subscribers(queue_id, student_id, lab_id) VALUES (%s, %s, %s)''', (queue_id, student_id, lab_id))
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)

    def sign_out_queue(self, *, queue_id: str, student_id: int, lab_id: str) -> None:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''DELETE FROM queues_subscribers WHERE queue_id = %s AND student_id = %s AND lab_id = %s''', (queue_id, student_id, lab_id))
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)

    def rate_student(self, *, student_id: int, lab_id: str, is_passed: bool) -> None:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''
                           INSERT INTO labs_results(lab_id, student_id, attempts_count, is_passed)
                           VALUES (%s, %s, 1, %s)
                           ON CONFLICT(lab_id, student_id) DO UPDATE
                           SET attempts_count = labs_results.attempts_count + 1, is_passed = EXCLUDED.is_passed
                           ''', (lab_id, student_id, str(is_passed)))
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)

    def get_student_passed_labs_count(self, *, group_id: str, student_id: int) -> int:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''
                           SELECT COUNT(*)
                           FROM labs_results
                           JOIN labs
                           ON labs_results.lab_id = labs.id
                           WHERE is_passed = True AND student_id = %s AND group_id = %s
                           ''', (student_id, group_id))
            rows = cursor.fetchall()
            assert len(rows) == 1
            result = rows[0][0]
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)
        return result

    def get_student_lab_attempts_count(self, *, student_id: int, lab_id: str) -> int:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''
                           SELECT attempts_count
                           FROM labs_results
                           WHERE lab_id = %s AND student_id = %s
                           LIMIT 1
                           ''', (lab_id, student_id))
            rows = cursor.fetchall()
            result = rows[0][0] if len(rows) == 1 else 0
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)
        return result

    def create_comparator(self, *, comparator: Comparator) -> None:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            data_str = "{"
            for i in range(len(comparator.data)):
                if i != 0:
                    data_str += ", "
                data_str += str(comparator.data[i].value[0])
            data_str += "}"
            cursor.execute('''
                           INSERT INTO comparators(id, owner_id, name, data) VALUES (%s, %s, %s, %s)
                           ''', (comparator.id, comparator.owner_id, comparator.name, data_str))
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)

    def delete_comparator(self, *, comparator_id: str) -> None:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''DELETE FROM comparators WHERE id = %s AND owner_id IS NOT NULL''', (comparator_id, ))
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)

    def get_comparator(self, *, comparator_id: str) -> Comparator:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''
                           SELECT id, owner_id, name, data
                           FROM comparators
                           WHERE id = %s
                           LIMIT 1
                           ''', (comparator_id, ))
            rows = cursor.fetchall()
            assert len(rows) == 1
            row = rows[0]
            result = Comparator(id=row[0], owner_id=row[1], name=row[2], data=row[3])
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)
        return result

    def get_teacher_comparators(self, *, teacher_id: int) -> tp.List[BriefComparator]:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''
                           SELECT id, name
                           FROM comparators
                           WHERE owner_id = %s
                           ''', (teacher_id, ))
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append(BriefComparator(id=row[0], name=row[1]))
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)
        return result

    def get_system_comparators(self) -> tp.List[BriefComparator]:
        psql_connection = self.__connection_pool.getconn()
        with psql_connection.cursor() as cursor:
            cursor.execute('''
                           SELECT id, name
                           FROM comparators
                           WHERE owner_id IS NULL
                           ''')
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append(BriefComparator(id=row[0], name=row[1]))
            psql_connection.commit()
        self.__connection_pool.putconn(psql_connection)
        return result