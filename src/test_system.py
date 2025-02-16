import os
import sys
from datetime import datetime
import pandas as pd
import torch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_data_collection():
    """Test if data collection is working"""
    print("\n1. Testing Data Collection...")
    
    # Check if data directory exists
    if not os.path.exists('training_data/stocks'):
        print("❌ Data directory not found. Please run auto_data_collector.py first")
        return False
        
    # Check if we have stock data
    stock_files = os.listdir('training_data/stocks')
    if not stock_files:
        print("❌ No stock data found")
        return False
        
    # Check data freshness
    sample_file = os.path.join('training_data/stocks', stock_files[0])
    df = pd.read_csv(sample_file)
    latest_date = pd.to_datetime(df.index[-1])
    days_old = (datetime.now() - latest_date).days
    
    if days_old > 5:  # Allowing for weekends
        print(f"⚠️ Data might be outdated ({days_old} days old)")
    else:
        print("✅ Data is up to date")
    
    print(f"✅ Found data for {len(stock_files)} stocks")
    return True

def test_models():
    """Test if models are working"""
    print("\n2. Testing Models...")
    
    # Check if model files exist
    if not os.path.exists('ai_models/price_model.pth'):
        print("❌ Price prediction model not found. Please train the model first")
        return False
        
    try:
        # Try to load the model
        from ai.models.price_model import PricePredictor
        model = PricePredictor()
        model.load_state_dict(torch.load('ai_models/price_model.pth'))
        print("✅ Successfully loaded price prediction model")
    except Exception as e:
        print(f"❌ Error loading model: {str(e)}")
        return False
    
    return True

def test_predictions():
    """Test if predictions are working"""
    print("\n3. Testing Predictions...")
    
    try:
        from ai.trading_system import TradingSystem
        
        # Initialize system
        system = TradingSystem()
        
        # Test prediction
        prediction = system.predict('RELIANCE')
        if prediction:
            print("\nSample Prediction for RELIANCE:")
            print(f"Current Price: ₹{prediction['current_price']:.2f}")
            print(f"Predicted Price: ₹{prediction['predicted_price']:.2f}")
            print(f"Expected Change: {prediction['change_percent']:.2f}%")
            print("\n✅ Prediction system is working")
            return True
        else:
            print("❌ Could not make prediction")
            return False
            
    except Exception as e:
        print(f"❌ Error making prediction: {str(e)}")
        return False

def main():
    print("Testing FamilyHVSDN Trading System\n" + "="*40)
    
    # Test each component
    data_ok = test_data_collection()
    if not data_ok:
        print("\n❌ Data collection test failed. Please fix before continuing")
        return
        
    models_ok = test_models()
    if not models_ok:
        print("\n❌ Model test failed. Please fix before continuing")
        return
        
    pred_ok = test_predictions()
    if not pred_ok:
        print("\n❌ Prediction test failed. Please fix before continuing")
        return
        
    print("\n" + "="*40)
    print("✅ All systems are working correctly!")
    print("""
Next Steps:
1. Start data collector: python src/ai/data_collection/auto_data_collector.py
2. Train models: python src/ai/training/train_price.py
3. Make predictions: python src/ai/trading_system.py
    """)

if __name__ == "__main__":
    main()
