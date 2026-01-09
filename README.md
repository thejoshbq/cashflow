# Budget Cashflow Visualizer

A powerful web-based personal finance tool for visualizing monthly cash flow using interactive Sankey diagrams. Track your income, expenses, savings, and assets with real-time visual feedback and future projections.

## Features

### 🔄 Interactive Cash Flow Visualization
- **Sankey Diagram**: Visual representation of money flowing from income through various categories to final destinations (expenses, savings, investments)
- **Color-coded nodes**: Instantly identify different budget categories
  - 🟢 Income sources
  - 🟢 Savings/Investments (dark green)
  - 🔴 Expenses
  - 🔵 Holding/Intermediate accounts
  - 🟠 Unallocated surplus
  - ⚠️ Red highlights for over-allocated categories

### 📊 Real-time Budget Analytics
- **Expense Gauge**: Visual indicator showing expenses as a percentage of income
  - Green (0-80%): Healthy spending
  - Yellow (80-100%): Warning zone
  - Red (>100%): Over budget
- **Budget Summary**: At-a-glance view of income, allocations, surplus/deficit
- **Over-allocation Warnings**: Automatic detection when you've allocated more than available

### 💰 Savings Projection
- Model future savings growth with compound interest
- Track multiple savings accounts simultaneously
- Adjustable time horizons (up to 240 months)
- Visual projection charts showing individual and combined savings trajectories

### 🏦 Asset Tracking
- Track standalone assets (property, investments, etc.)
- Pie chart visualization of asset distribution
- Separate from monthly cash flow for cleaner budgeting

### 🎯 Hierarchical Budget Structure
- Build multi-level budget hierarchies
- Create intermediate holding accounts
- Split expenses into detailed subcategories
- Full CRUD operations on all budget nodes

## Architecture

### Backend (FastAPI + Python)
```
src/cashflow/
├── main.py                 # FastAPI application entry point
├── core/
│   └── manager.py          # BudgetManager - core business logic
├── models/
│   └── node.py             # Node data structure for budget hierarchy
├── schemas/
│   └── schemas.py          # Pydantic models for API validation
└── api/v1/
    ├── budget_routes.py    # Budget endpoints (start, income, data)
    ├── node_routes.py      # Node CRUD endpoints
    └── asset_routes.py     # Asset management endpoints
```

### Frontend (Vanilla JavaScript + Plotly.js)
- Single-page application in `src/cashflow/static/index.html`
- Interactive UI with real-time updates
- Responsive visualizations using Plotly.js
- RESTful API consumption

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Clone the repository**
```bash
cd /home/otis-lab/Desktop/cashflow
```

2. **Create and activate virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

3. **Install dependencies**
```bash
pip install fastapi uvicorn plotly pydantic
```

Alternatively, create a `requirements.txt`:
```txt
fastapi>=0.128.0
uvicorn>=0.40.0
plotly>=6.5.1
pydantic>=2.12.5
```

Then install:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Server

Run the development server:
```bash
uvicorn src.cashflow.main:app --reload
```

Or with custom host/port:
```bash
uvicorn src.cashflow.main:app --host 0.0.0.0 --port 8000 --reload
```

The application will be available at:
- **Web UI**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Web Interface Workflow

1. **Initialize Budget**: Enter your monthly income and click "Start"
2. **Add Budget Nodes**: 
   - Select parent category
   - Name the node (e.g., "Rent", "Groceries", "401k")
   - Set monthly amount
   - Choose category type (Expense, Savings, Intermediate, Holding)
   - For savings: enter APR and current balance
3. **View Visualizations**: Charts update automatically
4. **Add Projections**: Enter months (e.g., 60 for 5-year projection)
5. **Track Assets**: Add standalone assets like property or investments

### Budget Node Types

| Type | Purpose | Example |
|------|---------|---------|
| **Income** | Root node (auto-created) | Your salary |
| **Intermediate** | Split flows to subcategories | "Living Expenses" → Rent, Utilities, Food |
| **Savings** | Accumulating accounts with interest | 401k, Emergency Fund, HSA |
| **Expense** | Final destination - money leaves | Rent, Groceries, Entertainment |
| **Holding** | Temporary holding for allocation | Checking Account |
| **Unallocated** | Auto-generated surplus | Leftover unallocated income |

## API Reference

### Budget Endpoints

#### Start Budget
```http
POST /api/v1/budget/start
Content-Type: application/json

{
  "income": 5000.00
}
```

#### Update Income
```http
PUT /api/v1/budget/income
Content-Type: application/json

{
  "income": 5500.00
}
```

#### Get Visualization Data
```http
GET /api/v1/budget/data?projection_months=60
```

**Response**: Complete visualization data including Sankey, gauge, pie charts, and projections

### Node Endpoints

#### Add Node
```http
POST /api/v1/nodes
Content-Type: application/json

{
  "parent_label": "Income",
  "label": "Retirement",
  "amount": 500.00,
  "group": "savings",
  "apr": 7.0,
  "current_balance": 10000.00
}
```

#### Edit Node
```http
PUT /api/v1/nodes/{label}
Content-Type: application/json

{
  "new_label": "Roth IRA",
  "new_amount": 600.00,
  "apr": 8.0
}
```

#### Delete Node
```http
DELETE /api/v1/nodes/{label}
```

#### List All Nodes
```http
GET /api/v1/nodes
```

### Asset Endpoints

#### Add Asset
```http
POST /api/v1/assets
Content-Type: application/json

{
  "name": "Home Equity",
  "value": 250000.00
}
```

#### Delete Asset
```http
DELETE /api/v1/assets/{name}
```

#### List Assets
```http
GET /api/v1/assets
```

## Example Budget Structure

```
Income ($6,000)
├── Savings ($1,200) [20%]
│   ├── 401k ($600) @ 7% APR
│   ├── Emergency Fund ($400) @ 4% APR
│   └── Investment Account ($200) @ 10% APR
├── Living Expenses ($3,000) [50%]
│   ├── Rent ($1,500)
│   ├── Utilities ($200)
│   ├── Groceries ($800)
│   └── Transportation ($500)
├── Discretionary ($800) [13%]
│   ├── Entertainment ($300)
│   ├── Dining Out ($300)
│   └── Hobbies ($200)
└── Unallocated Surplus ($1,000) [17%]
```

## Development

### Project Structure Details

**Core Components**:
- `BudgetManager`: Singleton managing entire budget state
- `Node`: Tree structure representing budget hierarchy
- Each node can have:
  - Children with flow values
  - Properties (APR, balance for savings)
  - Group classification

**Key Algorithms**:
- DFS traversal with priority sorting for visual grouping
- Real-time over-allocation detection
- Compound interest projections for savings
- Dynamic Sankey link generation

### Adding Features

To extend the application:

1. **New node types**: Update `priority` dict in `manager.py` and add colors
2. **New visualizations**: Add Plotly charts in `get_visualization_data()`
3. **Additional node properties**: Extend `Node.properties` and schemas
4. **New API endpoints**: Create new routers in `api/v1/`

### Testing

Run the application and test via:
- Interactive Swagger docs at `/docs`
- Web interface at `/`
- Direct API calls using curl or Postman

## Configuration

### CORS Settings
By default, the API allows all origins. For production, modify `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Static Files
Place your custom frontend in `src/cashflow/static/` to override the default interface.

## Troubleshooting

### Common Issues

**Port already in use**:
```bash
uvicorn src.cashflow.main:app --port 8001
```

**Module not found errors**:
Ensure you're running from the project root and the virtual environment is activated.

**Visualization not updating**:
Check browser console for API errors. Verify the API is running at the expected URL.

**Over-allocation warnings**:
Review your budget hierarchy - child allocations cannot exceed parent available amounts.

## Future Enhancements

Potential features for expansion:
- [ ] Data persistence (SQLite/PostgreSQL)
- [ ] User authentication and multi-user support
- [ ] Budget templates and presets
- [ ] CSV/Excel import/export
- [ ] Historical tracking and trends
- [ ] Bill reminders and recurring transactions
- [ ] Mobile-responsive design improvements
- [ ] Dark mode toggle
- [ ] Multiple currency support
- [ ] Budget comparison (planned vs. actual)

## License

This project is available for personal use and modification.

## Contributing

Feel free to fork, modify, and submit pull requests. For major changes, please open an issue first to discuss proposed changes.

## Contact

For questions or suggestions, please open an issue in the repository.

---

**Built with**: FastAPI, Plotly.js, Python, and ❤️
