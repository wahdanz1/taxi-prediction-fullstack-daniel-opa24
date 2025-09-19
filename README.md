# OPA24 - AI Engineering, Lab 1: TaxiPred

This is the first lab of the AI Engineering/OOP Advanced course in my programming education.

TaxiPred is an app with the goal functionality to be able to predict taxi trip prices with high accuracy. It is currently under development and will in the end contain the following features:

## 🎯 Planned Features

- **Price Prediction**: ML-powered taxi fare estimation based on distance, time, and location
- **Multi-page Dashboard**: User-friendly Streamlit interface with dedicated pages for predictions and model analysis
- **Location Integration**: Automatic distance calculation between pickup and dropoff locations
- **Model Performance Visualization**: Interactive charts showing model comparison for stakeholders
- **REST API**: FastAPI backend with comprehensive endpoints
- **Data Processing**: Robust data handling and feature engineering
- **Model Training**: Automated ML pipeline with scikit-learn
- **Validation**: Data validation using Pydantic models

## 🛠️ Tech Stack

- **Backend**: FastAPI - Modern, fast web framework for APIs
- **Machine Learning**: scikit-learn - ML model training and predictions
- **Data Validation**: Pydantic - Type validation and serialization
- **Frontend**: Streamlit - Interactive web dashboard
- **Environment**: UV - Modern Python dependency management

## 📁 Project Structure

```
taxipred/
├── explorations/
│   └── eda.ipynb              # Exploratory data analysis
├── src/taxipred/
│   ├── backend/
│   │   ├── api.py              # FastAPI application
│   │   ├── data_processing.py  # Data handling & preprocessing
│   │   ├── train_model.py      # ML model training pipeline
│   │   └── __init__.py
│   ├── frontend/
│   │   ├── dashboard.py        # Main Streamlit app
│   │   ├── pages/
│   │   │   ├── 1_Price_Prediction.py    # Price estimation page
│   │   │   ├── 2_Model_Performance.py   # Model analysis for stakeholders
│   │   │   └── 3_Data_Explorer.py       # Dataset insights
│   │   └── utils/
│   │       ├── api_client.py   # FastAPI integration
│   │       └── helpers.py      # Shared frontend functions
│   ├── data/
│   │   ├── taxi_trip_pricing.csv       # Original dataset
│   │   └── taxi_trip_pricing_clean.csv # Processed dataset
│   └── utils/
│       ├── constants.py        # Project constants
│       ├── helpers.py          # Utility functions
│       └── __init__.py
├── start.ps1                   # Launch script
├── pyproject.toml             # Project dependencies
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- UV (recommended) or pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd taxipred
   ```

2. **Set up environment**
   ```bash
   uv sync
   ```

3. **Launch the application**
   ```bash
   # Windows PowerShell
   .\start.ps1
   
   # Or manually:
   # Terminal 1 - Backend
   cd src/taxipred/backend
   uvicorn api:app --reload
   
   # Terminal 2 - Frontend
   streamlit run src/taxipred/frontend/dashboard.py
   ```

### Access Points
- **Streamlit Dashboard**: http://localhost:8501
  - **Homepage**: Overview and navigation
  - **Price Prediction**: Main fare estimation tool
  - **Model Performance**: Analysis dashboard for stakeholders
  - **Data Explorer**: Dataset insights and visualizations
- **FastAPI Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📊 Dataset

The project uses taxi trip pricing data containing features such as:
- Trip distance and duration
- Pickup and dropoff locations
- Time and date information
- Weather conditions
- Traffic patterns

## 🧠 Machine Learning Pipeline

1. **Data Preprocessing**: Clean and prepare raw taxi data
2. **Feature Engineering**: Extract relevant features for prediction
3. **Model Training**: Train ML models using scikit-learn
4. **Evaluation**: Assess model performance and accuracy
5. **Deployment**: Serve predictions via FastAPI

## 🎓 Learning Objectives

This lab focuses on:
- Building production-ready ML applications
- API development with FastAPI
- Data validation with Pydantic
- Interactive dashboards with Streamlit
- Modern Python project structure
- Dependency management with UV

## 📈 Current Status

🚧 **Under Development**

- [x] Project structure setup
- [x] Exploratory data analysis (EDA)
- [x] Data cleaning and preprocessing
- [x] ML model training and evaluation
- [x] Multi-page Streamlit frontend structure
- [ ] Frontend user interface implementation
- [ ] Location API integration for distance calculation
- [ ] FastAPI backend endpoints
- [ ] Pydantic data validation models
- [ ] API integration with frontend
- [ ] Model deployment and prediction serving
- [ ] Testing suite

## 🤝 Contributing

This is an educational project. Feedback and suggestions are welcome!

## 📝 License

Educational project - part of OPA24 AI Engineering course.
