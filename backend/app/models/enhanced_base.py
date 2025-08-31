from sqlalchemy.orm import declarative_base

# Enhanced base class for all enhanced models
# This separates the enhanced models from the original models
# to avoid conflicts in the SQLAlchemy registry

EnhancedBase = declarative_base()