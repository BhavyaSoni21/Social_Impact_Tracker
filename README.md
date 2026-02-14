# Social Impact Tracker

A nonprofit analytics system designed to collect, optimize, and evaluate program-level data to generate measurable impact insights.

## Overview

Many nonprofit organizations struggle with unstructured data, redundant storage, and unclear performance evaluation metrics. The Social Impact Tracker addresses these challenges by providing a structured platform to input program data and automatically compute meaningful impact metrics. The system features built-in data compression techniques, automated analytics, and an interactive dashboard for real-time insights.

This lightweight, scalable solution is specifically designed for small to medium-sized nonprofits seeking to make data-driven decisions and clearly demonstrate their social impact.

---

## 🎯 Key Features

### 📊 Program Data Management

Comprehensive program record management with structured data entry:

- **Program Name** - Unique identifier for each initiative
- **Time Period** - Duration or timeframe of program operation
- **Number of Beneficiaries** - People served by the program
- **Cost Incurred** - Operational expenses
- **Pre-Outcome Score** - Baseline metrics before program intervention
- **Post-Outcome Score** - Results after program completion

All data is stored in a relational database with full CRUD operations.

### 🗜️ Basic Data Compression Layer

Optimized data storage to reduce redundancy and improve efficiency:

- **Dictionary Encoding** - Compresses repeated program identifiers
- **Delta Encoding** - Efficiently stores time-series beneficiary growth data
- **Automated Compression** - Applied transparently during data storage
- **Reduced Storage Footprint** - Minimizes database size without loss of information

### 📈 Impact Metrics Engine

Automatic computation of key performance indicators:

| Metric | Formula | Purpose |
|--------|---------|---------|
| **Outcome Improvement** | Post-Outcome – Pre-Outcome | Measures program effectiveness |
| **Cost per Beneficiary** | Cost / Beneficiaries | Evaluates resource efficiency |
| **Growth Rate** | (Current – Previous) / Previous | Tracks program expansion |
| **Composite Impact Score** | Weighted formula combining all metrics | Overall program ranking |

All metrics are calculated automatically upon data entry and updated in real-time.

### 📉 Interactive Dashboard

Professional data visualization for quick insights:

- **Summary Statistics**
  - Total number of programs
  - Total beneficiaries served
  - Average impact score across all programs

- **Trend Visualizations**
  - Line chart showing beneficiary growth over time
  - Bar chart comparing cost vs. outcome improvement
  - Program ranking table sorted by impact score

- **Real-Time Updates** - Dashboard refreshes automatically with new data

### 🔌 API-Based Data Flow

RESTful API architecture for flexible integration:

- `POST /programs` - Submit new program data
- `GET /programs` - Retrieve all programs
- `GET /programs/{id}` - Get specific program details
- `GET /metrics/{id}` - Calculate metrics for a program
- `GET /analytics` - Retrieve aggregated analytics

Clean separation between frontend and backend enables future integrations.

### ✅ Data Validation

Robust validation ensures data integrity:

- Prevents negative or zero values for beneficiaries and costs
- Validates outcome score consistency (post-outcome ≥ pre-outcome when expected)
- Enforces required field completion
- Provides clear error messages for invalid inputs
- Maintains referential integrity in the database

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend Framework** | FastAPI | High-performance REST API |
| **Frontend/Dashboard** | Streamlit | Interactive web interface |
| **Database** | SQLite | Lightweight relational storage |
| **Data Processing** | Pandas, NumPy | Analytics and metrics computation |
| **Visualization** | Matplotlib/Plotly | Charts and graphs via Streamlit |
| **Compression** | Custom Python | Dictionary and delta encoding |
| **Language** | Python 3.9+ | Core development language |

---

## 🏗️ Architecture Overview

The system follows a modular, layered architecture:

```
┌─────────────────────────────────────────┐
│     Streamlit Frontend (Dashboard)       │
│   - User Interface                       │
│   - Data Visualization                   │
│   - Interactive Charts                   │
└─────────────────┬───────────────────────┘
                  │
                  │ REST API Calls
                  │
┌─────────────────▼───────────────────────┐
│         FastAPI Backend                  │
│   - API Endpoints                        │
│   - Business Logic                       │
│   - Data Validation                      │
└─────────────────┬───────────────────────┘
                  │
                  │
┌─────────────────▼───────────────────────┐
│  Compression & Analytics Engine          │
│   - Dictionary Encoding                  │
│   - Delta Encoding                       │
│   - Metrics Calculation                  │
└─────────────────┬───────────────────────┘
                  │
                  │
┌─────────────────▼───────────────────────┐
│       SQLite Database                    │
│   - Program Records                      │
│   - Compressed Data                      │
│   - Computed Metrics                     │
└─────────────────────────────────────────┘
```

### Design Principles

- **Separation of Concerns** - Clear boundaries between UI, logic, and data layers
- **Modularity** - Each component can be developed and tested independently
- **Scalability** - Architecture supports future expansion and feature additions
- **Maintainability** - Clean code structure with well-defined interfaces

---

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- 50MB free disk space

---

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Social_Impact_Tracker
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Usage

### Starting the Backend API

```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation (Swagger UI): `http://localhost:8000/docs`

### Starting the Dashboard

In a separate terminal:

```bash
streamlit run frontend/dashboard.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

---

## 📖 User Guide

### Adding a New Program

1. Navigate to the dashboard
2. Fill in the program entry form:
   - Enter program name
   - Select time period
   - Input number of beneficiaries
   - Enter total program cost
   - Provide pre and post-outcome scores
3. Click "Submit Program"
4. View automatically calculated metrics

### Viewing Analytics

- **Summary Cards** display quick statistics at the top
- **Growth Trends** show beneficiary expansion over time
- **Cost Analysis** compares spending to outcome improvements
- **Program Rankings** identify top-performing initiatives

### Interpreting Metrics

- **Outcome Improvement** - Higher is better; shows program effectiveness
- **Cost per Beneficiary** - Lower is better; indicates efficiency
- **Growth Rate** - Positive values show expansion
- **Composite Impact Score** - Normalized score for comparing programs

---

## 🗂️ Project Structure

```
Social_Impact_Tracker/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Data models
│   ├── database.py          # Database connection
│   ├── compression.py       # Compression algorithms
│   └── analytics.py         # Metrics calculation
├── frontend/
│   ├── dashboard.py         # Streamlit dashboard
│   └── utils.py             # Helper functions
├── tests/
│   ├── test_api.py          # API tests
│   ├── test_compression.py  # Compression tests
│   └── test_analytics.py    # Analytics tests
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

---

## 🔧 Configuration

Database and application settings can be configured in `backend/config.py`:

- Database path
- API host and port
- Compression thresholds
- Metric calculation weights

---

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=backend --cov=frontend tests/
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Built to support nonprofit organizations in their mission to create positive social change
- Designed with input from nonprofit program managers and data analysts
- Inspired by the need for accessible, actionable impact measurement tools

---

## 📞 Support

For questions, issues, or feature requests:

- Open an issue on GitHub
- Contact the development team
- Review documentation at `http://localhost:8000/docs` when running the API

---

## 🗺️ Roadmap

Future enhancements under consideration:

- [ ] Multi-user authentication and role-based access
- [ ] Export reports to PDF and Excel
- [ ] Advanced compression algorithms
- [ ] Machine learning for predictive impact analysis
- [ ] Integration with external nonprofit databases
- [ ] Mobile-responsive dashboard
- [ ] Multi-language support

---

**Made with ❤️ to empower nonprofits through data-driven insights**
