# CRDS Architecture

Cognitive Ransomware Defense System (CRDS) is a lightweight Endpoint Detection and Response (EDR) platform built with Django, React, and scikit-learn.

## Detection Pipeline

```
Filesystem Event (watchdog)
        ↓
Process Attribution (psutil)
        ↓
Feature Extraction (24-dim vector)
        ↓
ML Inference (joblib models)
        ↓
Rule Engine (heuristics + burst detection)
        ↓
Hybrid Scoring (AI + rules + honeypot + YARA + intel)
        ↓
Threat Creation + Alert
        ↓
Automated Response (configurable, dry-run default)
        ↓
WebSocket Broadcast + Dashboard
```

## Components

| Layer | Module | Purpose |
|-------|--------|---------|
| Monitoring | `apps/monitoring` | Recursive filesystem watchdog |
| Features | `feature_extraction/` | Behavioral feature engineering |
| Detection | `apps/detection` | Hybrid ML + rules pipeline |
| Deception | `apps/deception` | Honeypot generation and triggers |
| API | `apps/api` | REST + JWT + WebSocket |
| Frontend | `frontend/` | React dashboard |
| Training | `training/` | Offline model training |
| Models | `saved_models/` | Versioned joblib artifacts |

## Quick Start

```bash
# Backend
pip install -r requirements.txt
python manage.py migrate
python training/train.py --model random_forest
python manage.py createsuperuser
python manage.py runserver

# Frontend
cd frontend && npm install && npm run dev
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CRDS_WATCH_PATHS` | `demo_files` | Comma-separated monitor paths |
| `CRDS_RECURSIVE_MONITORING` | `true` | Recursive directory watching |
| `CRDS_AUTO_START_MONITORING` | `false` | Start monitor on Django boot |
| `CRDS_THRESHOLD_HIGH` | `0.75` | High threat threshold |
| `CRDS_THRESHOLD_MEDIUM` | `0.5` | Medium threat threshold |
| `CRDS_RESPONSE_DRY_RUN` | `true` | Safe response mode |
| `CRDS_WEIGHT_AI` | `0.35` | AI weight in hybrid score |

## Model Training

```bash
python training/train.py --model random_forest
python training/train.py --model isolation_forest
python evaluation/evaluate.py
```

## Docker Deployment

```bash
docker compose up --build
```

## External Dependencies

- **Real labeled datasets**: Synthetic training data is included; production requires labeled behavioral logs.
- **YARA**: Install `yara-python` and add rules to `rules/yara/`.
- **Network isolation**: OS-level agent required for live network disconnect.
- **Windows Event Logs / Registry**: Platform-specific collectors not yet integrated.
