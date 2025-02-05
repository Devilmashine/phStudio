from setuptools import setup, find_packages

setup(
    name="app",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "sqlalchemy",
        "alembic",
        "aiosqlite",
    ],
) 