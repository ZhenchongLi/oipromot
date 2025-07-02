"""Main entry point for OfficeAI Prompt Project"""

import uvicorn
from src.oipromot.app import app
from src.oipromot.database import create_db_and_tables


def main():
    create_db_and_tables()
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
