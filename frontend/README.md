# MediRetrieve Frontend — React + Vite Dashboard

A light, professional medical literature search and analytics dashboard built with **React**, **Vite**, **Recharts**, and **Lucide React**.

---

## 🎨 Features & Deliverables

1. **Deliverable 1: Medical Document Search Interface (`/`)**
   - Query input with example search chips.
   - Retrieval model selector (`rrf`, `semantic`, `bm25`, `tfidf`).
   - Configurable top-k result count (5, 10, 20, 50).
   - Medical synonym expansion toggle.
   - Ranked result cards with score badges, document IDs, matched terms, component ranks (for RRF), and expandable document text.

2. **Deliverable 2: Performance Comparison Table (`/comparison`)**
   - Evaluated metrics table comparing all 4 models on Precision@10, Recall@10, MAP, and nDCG@10.
   - Automatic highlighting of the maximum score per metric column.
   - High-level KPI summary cards.
   - Detailed IR evaluation methodology guide.

3. **Deliverable 3: Precision-Recall Graph (`/evaluation`)**
   - Recharts line chart mapping Recall (X-axis) vs. Precision (Y-axis) across rank cutoffs $k \in [1..100]$.
   - Fully backed by genuine precomputed evaluation metrics from `GET /api/v1/evaluation/results?split=test`.
   - Interactive model toggling and custom tooltips.

4. **About & Methodology (`/about`)**
   - Detailed explanation of the NFCorpus benchmark dataset, retrieval algorithms, and academic disclaimer.

---

## 🚀 Running the Frontend

### 1. Installation
```powershell
cd frontend
npm install
```

### 2. Start Vite Development Server
```powershell
npm run dev
```
The application will run at [http://127.0.0.1:5173](http://127.0.0.1:5173).

### 3. Build for Production
```powershell
npm run build
```

---

## 🔌 API Integration

The frontend connects to the FastAPI backend at `http://127.0.0.1:8000` via `VITE_API_BASE_URL` defined in `.env.example`.

Backend endpoints consumed:
- `GET /api/v1/health` — Backend readiness indicator.
- `GET /api/v1/models` — Retrieval models metadata.
- `POST /api/v1/search` — Medical document search execution.
- `GET /api/v1/evaluation/results?split=test` — Benchmark comparison metrics & Precision-Recall curve points.
