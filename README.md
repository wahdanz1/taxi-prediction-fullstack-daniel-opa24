# TaxiPred 🚕 - AI-Powered Taxi Fare Prediction

**OPA24 - AI Engineering, Lab 1**

TaxiPred is a full-stack machine learning application that predicts taxi fare prices with high accuracy using advanced ML models and real-world factors like weather, traffic, and time patterns.

## ✨ Features

### 🎯 **Core Functionality**
- **Smart Price Prediction**: ML-powered fare estimation using distance, passenger count, pickup time, weather, and traffic conditions
- **Address Autocomplete**: Google Places API integration for seamless location input
- **Real-time Distance Calculation**: Automatic route distance computation via Google Distance Matrix API
- **Interactive Progress Tracking**: Smooth UI feedback during prediction process

### 📊 **Dashboard & Analytics**
- **Multi-page Streamlit Interface**: Professional dashboard with dedicated sections
- **Model Performance Visualization**: Interactive charts and metrics for stakeholders
- **Data Explorer**: Comprehensive dataset insights and analytics
- **Trip Summary**: Detailed breakdown of prediction factors

### 🔧 **Technical Features**
- **REST API**: Comprehensive FastAPI backend with full documentation
- **Data Validation**: Robust input validation using Pydantic models
- **Feature Engineering**: Advanced ML features including interaction terms and time-based variables
- **Model Persistence**: Trained model artifacts with metrics and feature importance
- **Error Handling**: Comprehensive error management and user feedback

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend API** | FastAPI | High-performance REST API with automatic documentation |
| **Frontend** | Streamlit | Interactive multi-page dashboard |
| **ML Framework** | scikit-learn | Model training, prediction, and evaluation |
| **Data Validation** | Pydantic | Type validation and serialization |
| **External APIs** | Google Places & Routes | Location services and distance calculation |
| **Package Management** | UV | Modern Python dependency management |
| **Data Processing** | pandas, joblib | Data manipulation and model persistence |

## 📁 Project Structure

```
taxipred/
├── explorations/
│   └── eda.ipynb                    # Exploratory data analysis
├── src/taxipred/
│   ├── backend/
│   │   ├── models/                  # Trained model artifacts
│   │   ├── api.py                   # FastAPI application with all endpoints
│   │   ├── data_processing.py       # Runtime ML pipeline and feature engineering
│   │   └── google_services.py       # Google APIs integration
│   ├── data/
│   │   ├── taxi_trip_pricing.csv        # Original dataset
│   │   └── taxi_trip_pricing_clean.csv  # Processed dataset
│   ├── frontend/
│   │   ├── pages/
│   │   │   ├── 1_Price_Prediction.py    # Main prediction interface
│   │   │   ├── 2_Data_Explorer.py       # Dataset exploration tools
│   │   │   └── 3_Model_Performance.py   # Model analytics dashboard
│   │   ├── dashboard.py            # Main Streamlit application
│   │   ├── styles.css              # Custom styling
│   │   ├── ui_components.py        # Reusable UI components
│   │   └── ui_helpers.py           # Frontend utility functions
│   ├── scripts/
│   │   ├── data_cleaning.py        # Advanced data cleaning pipeline
│   │   └── train_model.py          # Model training pipeline
│   └── utils/
│       ├── api_helpers.py          # API communication utilities
│       └── constants.py            # Project-wide constants
├── data_cleaning_summary.md        # Detailed data processing documentation
├── .env                            # Environment variables (create this!)
├── README.md
├── pyproject.toml                  # Project dependencies and metadata
├── start.ps1                       # Windows launcher script
└── uv.lock                         # UV dependencies file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- UV package manager (recommended) or pip
- Google Cloud API key for Places and Routes APIs

### Installation

1. **Clone and navigate to project**
   ```bash
   git clone https://github.com/wahdanz1/taxi-prediction-fullstack-daniel-opa24
   cd taxipred
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file in project root
   echo "GMAPS_API_KEY=your_google_api_key_here" > .env
   ```

4. **Train model and save joblib-files**
   ```bash
   # Run model training script
   python src/scripts/train_model.py
   ```

5. **Launch the application**
   ```bash
   # Windows PowerShell (recommended)
   .\start.ps1
   
   # Or launch manually:
   # Terminal 1 - Backend API
   cd src/taxipred/backend && uvicorn api:app --reload
   
   # Terminal 2 - Frontend Dashboard  
   streamlit run src/taxipred/frontend/dashboard.py
   ```

### 🌐 Access Points
- **📱 Streamlit Dashboard**: http://localhost:8501
- **🔌 FastAPI Backend**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs

## 🎯 Usage Guide

### Making Predictions
1. **Enter Locations**: Use suggestions for pickup and destination addresses
2. **Set Trip Details**: Choose date, time, and passenger count
3. **Get Estimate**: View real-time prediction with detailed breakdown
4. **Analyze Results**: Review factors considered in the prediction

### API Endpoints
- `GET /health` - API health check
- `GET /taxi` - Retrieve cleaned dataset
- `GET /taxi/stats` - Dataset statistics
- `POST /predict` - Generate fare prediction
- `POST /suggestion` - Get address suggestions
- `POST /distance` - Calculate trip distance & traffic conditions
- `POST /weater` - Calculate trip distance & traffic conditions

## 📊 Machine Learning Pipeline

### Advanced Data Processing
- **Cleaning methodology** with mathematical recovery and data leakage prevention
- **Sophisticated feature engineering** including weather/traffic multipliers and interaction terms
- **Honest performance evaluation** prioritizing legitimate prediction over artificially low error rates
- **Data retention**: 97.7% of original data retained through intelligent cleaning

*See [data_cleaning_summary.md](data_cleaning_summary.md) for detailed technical documentation*

### Model Architecture
- **Distance-based pricing**: Primary fare component (61% feature importance)
- **Interaction features**: `distance_x_conditions` captures complex weather/traffic relationships (37% feature importance)
- **Environmental factors**: Weather impact (Clear: 1.0, Rain: 1.15, Snow: 1.3) and traffic multipliers (Low: 1.0, Medium: 1.1, High: 1.25)
- **Time-based adjustments**: Rush hour detection, weekend patterns, peak hour identification
- **Top 3 features explain 98.7% of predictions**, demonstrating model efficiency

### Performance Metrics
- **Production Model**: GradientBoosting with $15.56 MAE, 0.828 R² (legitimate prediction without data leakage)
- **Model Comparison**: Outperformed LinearRegression ($17.00 MAE) and RandomForest ($15.91 MAE)
- **Test Set Performance**: 196 samples, consistent validation across multiple metrics
- **Production-ready artifacts**: Trained model, metrics, and feature importance saved for deployment

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
GMAPS_API_KEY=your_google_maps_api_key
```

### Google APIs Setup
1. Enable Google _Places API (New)_
2. Enable Google _Routes API_
3. Create API key with appropriate restrictions
4. Add billing information (required for production usage) - but these can be used with Free Tier

## 🎓 Learning Outcomes

This project demonstrates advanced ML engineering concepts:

### **Core ML Principles**
- **Data leakage detection and prevention** - avoiding "AI calculator" approaches
- **Feature engineering mastery** - creating meaningful interactions when raw signals prove weak
- **Domain knowledge application** - using business logic for data quality without compromising model integrity
- **Honest performance evaluation** - choosing legitimate prediction over competition metrics

### **Production Development**
- **Full-stack ML architecture** from data cleaning to user interface
- **Modern API design** with FastAPI, comprehensive validation, and error handling
- **Interactive dashboard development** with real-time feedback and progressive UI states
- **External service integration** with proper error handling and graceful degradation

### **Software Engineering**
- **Professional project organization** with modular design and proper dependency management
- **Advanced data processing** with iterative improvement and quality assurance
- **User experience focus** - designing for real-world inputs rather than perfect data
- **Documentation excellence** - separating concerns between README and technical details

## 📈 Project Status

### ✅ **Completed Features**
- [x] Complete ML pipeline with sophisticated data cleaning and feature engineering
- [x] FastAPI backend with comprehensive endpoints and validation
- [x] Multi-page Streamlit frontend with professional UI
- [x] Google APIs integration (Places New, Routes, and Weather APIs)
- [x] Real-time traffic prediction based on departure time
- [x] Real-time weather conditions for accurate fare estimation
- [x] Address autocomplete functionality with session state caching
- [x] Smooth progress tracking with animated UI transitions
- [x] Robust error handling with graceful degradation
- [x] Model persistence with metrics and feature importance tracking
- [x] Data exploration and model performance visualization pages
- [x] Rush hour detection with API prediction validation

## 🤝 Contributing

This is an educational project for my OOP/AI Programming Education. Feedback, suggestions, and improvements are welcome!

## 📄 License

Educational project - Part of my OOP/AI Programming Education coursework.

---

**Built with ❤️ using modern Python ML stack**