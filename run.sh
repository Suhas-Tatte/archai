#!/bin/bash

echo "🚀 Starting Archai setup..."

# 1. Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# 2. Activate venv
echo "⚙️ Activating virtual environment..."
source venv/bin/activate

# 3. Install dependencies
echo "📥 Installing requirements..."
pip install -r requirements.txt

# 4. Check .env
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Create a .env file with Neo4j credentials."
    exit 1
fi

# 5. Run ingestion
echo "📊 Loading data into Neo4j..."
python -m graph_layer.ingestion_data

echo "✅ Done! Open Neo4j Browser at http://localhost:7474"

# 6. Run llm
echo "🤖 Starting LLM..."
python -m llm.main

# 7. Run map
echo "🗺️ Starting Map..."
python -m scripts.map_demo