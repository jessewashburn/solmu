#!/bin/bash
# Build script for React frontend

cd frontend
npm install
npm run build

echo "Frontend build complete! Output in frontend/dist/"
