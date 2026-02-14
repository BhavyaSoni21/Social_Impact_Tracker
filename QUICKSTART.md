# Quick Start Guide - Social Impact Tracker

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies

Open PowerShell in the project directory and run:

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start the Application

**Option A: Use Quick Start Script (Recommended)**

```powershell
python quickstart.py
```

This will automatically start both the backend API and frontend dashboard.

**Option B: Start Services Manually**

*Terminal 1 - Backend:*
```powershell
uvicorn backend.main:app --reload
```

*Terminal 2 - Frontend:*
```powershell
streamlit run frontend/dashboard.py
```

### Step 3: Access the Application

- **Dashboard:** http://localhost:8501
- **API Documentation:** http://localhost:8000/docs
- **API Health Check:** http://localhost:8000/health

---

## 📖 Basic Usage

### Adding Your First Program

1. Open the dashboard at http://localhost:8501
2. Navigate to "Add Program" in the sidebar
3. Fill in the program details:
   - Program Name: "Youth Literacy Program"
   - Time Period: "2025-Q1"
   - Beneficiaries: 200
   - Cost: $15,000
   - Pre-Outcome Score: 45
   - Post-Outcome Score: 78
4. Click "Submit Program"

### Viewing Analytics

1. Navigate to "Dashboard" to see summary metrics
2. View charts showing:
   - Top programs by impact score
   - Cost vs outcome improvement
   - Beneficiary growth trends

### Using the API

**Create a Program:**
```powershell
$body = @{
    program_name = "Community Health Initiative"
    time_period = "2025-Q2"
    beneficiaries = 300
    cost = 25000
    pre_outcome_score = 50
    post_outcome_score = 85
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/programs" -Method POST -Body $body -ContentType "application/json"
```

**Get All Programs:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/programs" -Method GET
```

**Get Analytics Summary:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/analytics/summary" -Method GET
```

---

## 🧪 Running Tests

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/test_api.py
```

---

## 🔧 Troubleshooting

### Port Already in Use

If port 8000 or 8501 is already in use:

```powershell
# For backend (change port)
uvicorn backend.main:app --reload --port 8001

# For frontend (change port)
streamlit run frontend/dashboard.py --server.port 8502
```

### Module Not Found Error

Make sure you're in the project root directory and virtual environment is activated:

```powershell
cd C:\Projects\Social_Impact_Tracker
.\venv\Scripts\activate
```

### Database Issues

To reset the database:

```powershell
# Delete the database file
Remove-Item -Path data\social_impact.db -Force

# Restart the API (database will be recreated)
uvicorn backend.main:app --reload
```

---

## 📊 Understanding Impact Metrics

### Outcome Improvement
**Formula:** Post-Outcome Score - Pre-Outcome Score  
**Interpretation:** Higher is better. Shows program effectiveness.

### Cost per Beneficiary
**Formula:** Total Cost / Number of Beneficiaries  
**Interpretation:** Lower is better. Shows resource efficiency.

### Growth Rate
**Formula:** (Current Beneficiaries - Previous) / Previous  
**Interpretation:** Positive shows expansion, negative shows contraction.

### Composite Impact Score
**Formula:** Weighted combination of all metrics (0-100)  
**Interpretation:** Higher is better. Overall program performance.

**Weights:**
- Outcome Improvement: 40%
- Cost Efficiency: 35%
- Growth Rate: 25%

---

## 🎯 Next Steps

1. **Add More Programs:** Build your dataset with multiple programs
2. **Explore Analytics:** Use the dashboard to compare program performance
3. **Customize Metrics:** Edit `backend/config.py` to adjust metric weights
4. **Integrate with Tools:** Use the REST API to integrate with other systems
5. **Export Data:** Use the API to extract data for reporting

---

## 📚 Additional Resources

- **API Documentation:** http://localhost:8000/docs
- **Project README:** See README.md for detailed information
- **Configuration:** Edit `backend/config.py` for customization

---

## 💡 Pro Tips

1. Use the API documentation (Swagger UI) to test endpoints interactively
2. Add programs with different time periods to see growth trends
3. Export data via API for integration with Excel or other tools
4. Run tests before making custom modifications
5. Check the compression stats endpoint for storage efficiency metrics

---

**Need Help?** Check the main README.md or open an issue on GitHub.
