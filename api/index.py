"""
api/index.py — Vercel Serverless Function entry point
Exposes the Flask app instance for Vercel's Python runtime.
"""
import sys
import os

# Ensure the root project directory is on sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import app

# Vercel's Python WSGI handler picks up `app`
if __name__ == "__main__":
    app.run()
