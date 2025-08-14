"""
🗄️ Initial Database Schema Migration
Creates the basic tables for the finance chatbot system
"""


def migrate(cursor, connection):
    """
    Execute the migration
    """
    logger.info("🔄 Creating initial database schema...")

    # Create users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    logger.info("✅ Users table created")

    # Create chat_sessions table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) UNIQUE NOT NULL,
            user_id INTEGER REFERENCES users(id),
            title VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    logger.info("✅ Chat sessions table created")

    # Create chat_messages table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) REFERENCES chat_sessions(session_id),
            role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
            content TEXT NOT NULL,
            response TEXT,
            context JSONB,
            source JSONB,
            confidence FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    logger.info("✅ Chat messages table created")

    # Create documents table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            file_path VARCHAR(500),
            file_size BIGINT,
            content_type VARCHAR(100),
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP,
            status VARCHAR(20) DEFAULT 'pending'
        )
    """
    )
    logger.info("✅ Documents table created")

    # Create embeddings table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS embeddings (
            id SERIAL PRIMARY KEY,
            document_id INTEGER REFERENCES documents(id),
            chunk_text TEXT NOT NULL,
            embedding_vector JSONB NOT NULL,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    logger.info("✅ Embeddings table created")

    # Create indexes for better performance
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id)
    """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id)
    """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_embeddings_document_id ON embeddings(document_id)
    """
    )
    logger.info("✅ Database indexes created")

    # Commit the transaction
    connection.commit()
    logger.info("🎉 Initial schema migration completed successfully")


def rollback(cursor, connection):
    """
    Rollback the migration
    """
    logger.info("🔄 Rolling back initial schema migration...")

    # Drop tables in reverse order (due to foreign key constraints)
    cursor.execute("DROP TABLE IF EXISTS embeddings CASCADE")
    cursor.execute("DROP TABLE IF EXISTS documents CASCADE")
    cursor.execute("DROP TABLE IF EXISTS chat_messages CASCADE")
    cursor.execute("DROP TABLE IF EXISTS chat_sessions CASCADE")
    cursor.execute("DROP TABLE IF EXISTS users CASCADE")

    # Commit the rollback
    connection.commit()
    logger.info("✅ Initial schema migration rolled back successfully")


# Migration metadata
MIGRATION_METADATA = {
    "version": "001",
    "name": "initial_schema",
    "description": "Create initial database schema for finance chatbot",
    "author": "NeuroGent Team",
    "created_at": "2025-01-14",
    "dependencies": [],
    "rollback_sql": """
        DROP TABLE IF EXISTS embeddings CASCADE;
        DROP TABLE IF EXISTS documents CASCADE;
        DROP TABLE IF EXISTS chat_messages CASCADE;
        DROP TABLE IF EXISTS chat_sessions CASCADE;
        DROP TABLE IF EXISTS users CASCADE;
    """,
}
