@echo off

echo 🚀 Starting Archai setup...

REM 1. Create virtual environment
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM 2. Activate venv
echo ⚙️ Activating virtual environment...
call venv\Scripts\activate

REM 3. Install requirements
echo 📥 Installing requirements...
pip install -r requirements.txt

REM 4. Check .env
if not exist .env (
    echo ❌ .env file not found!
    echo Create a .env file with Neo4j credentials.
    pause
    exit /b 1   
)

REM 5. Run ingestion
echo 📊 Loading data into Neo4j...
python -m graph_layer.ingestion_data

echo ✅ Done! Open Neo4j Browser at http://localhost:7474

REM 6. Run llm
echo 🤖 Starting LLM...
python -m llm.main

REM 7. Run map 
echo 🗺️ Starting Map...
python -m scripts.map_demo
pause