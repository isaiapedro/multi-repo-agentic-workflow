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
