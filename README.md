# 🌬️ AI-Based Pollution + Traffic Optimization System

An AI-powered smart city system that predicts pollution and suggests optimal travel routes to reduce environmental impact.

## Features

- ✅ Real-time AQI monitoring
- ✅ AI-powered AQI predictions (2-4 hours ahead)
- ✅ Smart route suggestions (low-pollution paths)
- ✅ Pollution alerts with threshold triggers
- ✅ Interactive heatmap visualization
- ✅ "Best time to travel" recommendations

## Tech Stack

- **Backend**: FastAPI, Python
- **AI/ML**: Scikit-learn, Random Forest
- **Frontend**: HTML, CSS, JavaScript, Leaflet.js
- **Database**: SQLite

## Setup

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and add your API keys
6. Train the model: `python -m backend.ml.train_model`
7. Run the server: `uvicorn backend.main:app --reload`
8. Open: [localhost](http://localhost:8000)

## API Endpoints

- `GET /api/aqi/{city}` - Get current AQI
- `GET /api/aqi/predict/{city}` - Get AQI predictions
- `GET /api/traffic/{city}` - Get traffic data
- `POST /api/routes/optimize` - Get optimized route
- `GET /api/alerts/{city}` - Get pollution alerts
