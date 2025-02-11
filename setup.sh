#!/bin/bash

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install poetry if not installed
if ! command -v poetry &> /dev/null; then
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Install dependencies
poetry install

# Create .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please update it with your tokens."
    rm .env.example
fi

# Create logs directory
mkdir -p logs data

echo "Setup completed! Activate virtual environment with: source .venv/bin/activate"