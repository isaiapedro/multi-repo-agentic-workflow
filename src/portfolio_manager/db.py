import logging

import psycopg2

from portfolio_manager.config import postgres_connection_kwargs

logger = logging.getLogger(__name__)


class OrchestratorDB:
    def __init__(self):
        self.conn = psycopg2.connect(**postgres_connection_kwargs())
        self.conn.autocommit = True
        self.setup_tables()

    def setup_tables(self):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS workflow_state (
                    run_id SERIAL PRIMARY KEY,
                    repo_name VARCHAR(255),
                    current_step VARCHAR(50),
                    status VARCHAR(20),
                    retry_count INT DEFAULT 0,
                    cost_usd FLOAT DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
        logger.info("Database tables verified.")

    def insert_new_run(self, repo_name: str, status: str) -> int:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO workflow_state (repo_name, current_step, status)
                VALUES (%s, %s, %s)
                RETURNING run_id
                """,
                (repo_name, "orchestrator", status),
            )
            row = cur.fetchone()
        return row[0]

    def update_run_status(self, repo_name: str, status: str) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE workflow_state
                SET status = %s, last_updated = CURRENT_TIMESTAMP
                WHERE run_id = (
                    SELECT MAX(run_id) FROM workflow_state WHERE repo_name = %s
                )
                """,
                (status, repo_name),
            )
