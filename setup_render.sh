#!/bin/bash
# Setup for Render.com deployment
echo "=== Setting up SHL Assessment for Render ==="

# 1. Create runtime.txt (CRITICAL)
echo "python-3.11.0" > runtime.txt
echo "✅ Created runtime.txt with Python 3.11.0"

# 2. Update requirements.txt
cat > requirements.txt << 'EOF'
# SHL Assessment - Render Compatible
# Using pre-built wheels for Python 3.11
pandas==2.1.4
numpy==1.24.3
scikit-learn==1.3.2
faiss-cpu>=1.13.1
fastapi==0.104.1
uvicorn[standard]==0.24.0
google-generativeai==0.3.0
requests==2.31.0
openpyxl==3.1.2
python-dotenv==1.0.0
EOF
echo "✅ Created requirements.txt with compatible versions"

# 3. Create .gitignore if missing
if [ ! -f .gitignore ]; then
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
    echo "✅ Created .gitignore"
fi

echo "=== Ready to deploy ==="
echo "1. Commit: git add . && git commit -m 'Render setup'"
echo "2. Push: git push origin main"
echo "3. Deploy: Go to Render.com → New Web Service"