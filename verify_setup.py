import os
import sys

def verify_setup():
    """Verify that the project is set up correctly"""
    
    print("🔍 Verifying Photo Studio CRM Setup...")
    print("=" * 50)
    
    # Check if required directories exist
    required_dirs = [
        "backend",
        "frontend",
        "backend/app",
        "frontend/src"
    ]
    
    print("📁 Checking directories:")
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✅ {directory}")
        else:
            print(f"  ❌ {directory}")
    
    print()
    
    # Check if required files exist
    required_files = [
        "backend/app/main.py",
        "frontend/src/App.tsx",
        "backend/requirements.txt",
        "package.json",
        ".env"
    ]
    
    print("📄 Checking files:")
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")
    
    print()
    
    # Check environment variables
    print("⚙️  Checking environment variables:")
    required_env_vars = [
        "DATABASE_URL",
        "SECRET_KEY"
    ]
    
    try:
        with open(".env", "r") as f:
            env_content = f.read()
        
        for var in required_env_vars:
            if var in env_content:
                print(f"  ✅ {var}")
            else:
                print(f"  ❌ {var}")
    except FileNotFoundError:
        print("  ❌ .env file not found")
    
    print()
    
    # Check Python dependencies
    print("🐍 Checking Python dependencies:")
    try:
        import fastapi
        print("  ✅ FastAPI")
    except ImportError:
        print("  ❌ FastAPI")
    
    try:
        import sqlalchemy
        print("  ✅ SQLAlchemy")
    except ImportError:
        print("  ❌ SQLAlchemy")
    
    try:
        import uvicorn
        print("  ✅ Uvicorn")
    except ImportError:
        print("  ❌ Uvicorn")
    
    print()
    
    # Check Node dependencies
    print("🟢 Checking Node dependencies:")
    if os.path.exists("node_modules"):
        print("  ✅ node_modules directory exists")
    else:
        print("  ⚠️  node_modules directory not found (run 'npm install')")
    
    if os.path.exists("package-lock.json"):
        print("  ✅ package-lock.json exists")
    else:
        print("  ❌ package-lock.json not found")
    
    print()
    print("✅ Setup verification complete!")

if __name__ == "__main__":
    verify_setup()