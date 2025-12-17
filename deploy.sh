#!/bin/bash
echo "=== DEPLOYING SHL ASSESSMENT SYSTEM ==="

# Create runtime.txt if it doesn't exist
if [ ! -f runtime.txt ]; then
    echo "python-3.11.0" > runtime.txt
    echo "✅ Created runtime.txt"
fi

# Update requirements.txt
cat > requirements.txt << EOF
# SHL Assessment System - Compatible with Python 3.11
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

echo "✅ Updated requirements.txt"
echo "=== READY TO DEPLOY ==="