from typing import Dict, List, Optional, Union, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
import optuna
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import joblib
import os
from ..utils.market_data import MarketData

class ModelManager:
    """AI model management and optimization system."""
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        self.market_data = MarketData()
        self.models = {}
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Ensure model directory exists
        os.makedirs(model_dir, exist_ok=True)
    
    async def train_model(self, model_type: str, symbol: str,
                         start_date: datetime,
                         end_date: datetime,
                         hyperparameters: Optional[Dict] = None) -> Dict:
        """Train an AI model for trading."""
        try:
            # Get training data
            data = await self._prepare_training_data(
                symbol, start_date, end_date
            )
            
            # Initialize model
            model = self._initialize_model(model_type, hyperparameters)
            
            # Train model
            if model_type == "price_prediction":
                metrics = await self._train_price_prediction_model(
                    model, data
                )
            elif model_type == "sentiment_analysis":
                metrics = await self._train_sentiment_model(model, data)
            elif model_type == "portfolio_optimization":
                metrics = await self._train_portfolio_model(model, data)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            # Save model
            model_path = self._save_model(model, model_type, symbol)
            
            return {
                "model_type": model_type,
                "symbol": symbol,
                "metrics": metrics,
                "model_path": model_path,
                "training_time": metrics.get("training_time", 0),
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"Error training model: {str(e)}")
            return {}
    
    async def optimize_model(self, model_type: str, symbol: str,
                           optimization_metric: str = "val_loss",
                           n_trials: int = 100) -> Dict:
        """Optimize model hyperparameters using Optuna."""
        try:
            study = optuna.create_study(
                direction="minimize" if "loss" in optimization_metric else "maximize"
            )
            
            # Define objective function
            async def objective(trial):
                # Generate hyperparameters
                hyperparameters = self._generate_hyperparameters(
                    trial, model_type
                )
                
                # Train model with hyperparameters
                result = await self.train_model(
                    model_type,
                    symbol,
                    datetime.now() - timedelta(days=365),
                    datetime.now(),
                    hyperparameters
                )
                
                return result["metrics"][optimization_metric]
            
            # Run optimization
            study.optimize(objective, n_trials=n_trials)
            
            # Get best parameters
            best_params = study.best_params
            best_value = study.best_value
            
            # Train final model with best parameters
            final_result = await self.train_model(
                model_type,
                symbol,
                datetime.now() - timedelta(days=365),
                datetime.now(),
                best_params
            )
            
            return {
                "best_parameters": best_params,
                "best_value": best_value,
                "optimization_history": study.trials_dataframe().to_dict(),
                "final_model": final_result,
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"Error optimizing model: {str(e)}")
            return {}
    
    async def evaluate_model(self, model_type: str, symbol: str,
                           start_date: datetime,
                           end_date: datetime) -> Dict:
        """Evaluate model performance on test data."""
        try:
            # Load model
            model = self._load_model(model_type, symbol)
            if not model:
                return {}
            
            # Get test data
            test_data = await self._prepare_training_data(
                symbol, start_date, end_date
            )
            
            # Evaluate model
            metrics = await self._evaluate_model_performance(
                model,
                model_type,
                test_data
            )
            
            return {
                "model_type": model_type,
                "symbol": symbol,
                "metrics": metrics,
                "evaluation_period": {
                    "start": start_date,
                    "end": end_date
                },
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"Error evaluating model: {str(e)}")
            return {}
    
    async def predict(self, model_type: str, symbol: str,
                     data: Optional[pd.DataFrame] = None) -> Dict:
        """Generate predictions using trained model."""
        try:
            # Load model
            model = self._load_model(model_type, symbol)
            if not model:
                return {}
            
            # Get data if not provided
            if data is None:
                data = await self._prepare_prediction_data(symbol)
            
            # Generate predictions
            if model_type == "price_prediction":
                predictions = await self._predict_prices(model, data)
            elif model_type == "sentiment_analysis":
                predictions = await self._predict_sentiment(model, data)
            elif model_type == "portfolio_optimization":
                predictions = await self._predict_portfolio_weights(model, data)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            return {
                "model_type": model_type,
                "symbol": symbol,
                "predictions": predictions,
                "confidence": self._calculate_prediction_confidence(predictions),
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"Error generating predictions: {str(e)}")
            return {}
    
    async def update_model(self, model_type: str, symbol: str,
                         new_data: pd.DataFrame) -> Dict:
        """Update existing model with new data."""
        try:
            # Load existing model
            model = self._load_model(model_type, symbol)
            if not model:
                return {}
            
            # Prepare new data
            prepared_data = await self._prepare_update_data(new_data)
            
            # Update model
            if model_type == "price_prediction":
                metrics = await self._update_price_model(model, prepared_data)
            elif model_type == "sentiment_analysis":
                metrics = await self._update_sentiment_model(
                    model, prepared_data
                )
            elif model_type == "portfolio_optimization":
                metrics = await self._update_portfolio_model(
                    model, prepared_data
                )
            
            # Save updated model
            model_path = self._save_model(model, model_type, symbol)
            
            return {
                "model_type": model_type,
                "symbol": symbol,
                "update_metrics": metrics,
                "model_path": model_path,
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"Error updating model: {str(e)}")
            return {}
    
    def _initialize_model(self, model_type: str,
                         hyperparameters: Optional[Dict] = None) -> nn.Module:
        """Initialize AI model based on type."""
        if model_type == "price_prediction":
            return self._create_price_prediction_model(hyperparameters)
        elif model_type == "sentiment_analysis":
            return self._create_sentiment_model(hyperparameters)
        elif model_type == "portfolio_optimization":
            return self._create_portfolio_model(hyperparameters)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    def _create_price_prediction_model(self,
                                     hyperparameters: Optional[Dict] = None) -> nn.Module:
        """Create price prediction model architecture."""
        class PricePredictionModel(nn.Module):
            def __init__(self, input_size, hidden_size, num_layers):
                super().__init__()
                self.lstm = nn.LSTM(
                    input_size,
                    hidden_size,
                    num_layers,
                    batch_first=True
                )
                self.fc = nn.Linear(hidden_size, 1)
            
            def forward(self, x):
                lstm_out, _ = self.lstm(x)
                predictions = self.fc(lstm_out[:, -1, :])
                return predictions
        
        hp = hyperparameters or {
            "input_size": 10,
            "hidden_size": 64,
            "num_layers": 2
        }
        
        return PricePredictionModel(**hp)
    
    def _create_sentiment_model(self,
                              hyperparameters: Optional[Dict] = None) -> nn.Module:
        """Create sentiment analysis model."""
        model = AutoModelForSequenceClassification.from_pretrained(
            "ProsusAI/finbert"
        )
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        return model
    
    def _create_portfolio_model(self,
                              hyperparameters: Optional[Dict] = None) -> nn.Module:
        """Create portfolio optimization model."""
        class PortfolioOptimizationModel(nn.Module):
            def __init__(self, input_size, hidden_size, num_assets):
                super().__init__()
                self.lstm = nn.LSTM(
                    input_size,
                    hidden_size,
                    batch_first=True
                )
                self.fc = nn.Linear(hidden_size, num_assets)
                self.softmax = nn.Softmax(dim=1)
            
            def forward(self, x):
                lstm_out, _ = self.lstm(x)
                weights = self.fc(lstm_out[:, -1, :])
                return self.softmax(weights)
        
        hp = hyperparameters or {
            "input_size": 10,
            "hidden_size": 64,
            "num_assets": 10
        }
        
        return PortfolioOptimizationModel(**hp)
    
    async def _prepare_training_data(self, symbol: str,
                                   start_date: datetime,
                                   end_date: datetime) -> pd.DataFrame:
        """Prepare data for model training."""
        # Get historical data
        data = await self.market_data.get_historical_data(
            symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        # Add technical indicators
        data = self._add_technical_indicators(data)
        
        # Normalize data
        scaler = StandardScaler()
        normalized_data = pd.DataFrame(
            scaler.fit_transform(data),
            columns=data.columns,
            index=data.index
        )
        
        return normalized_data
    
    def _add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to dataset."""
        df = data.copy()
        
        # Moving averages
        df["SMA_20"] = df["Close"].rolling(window=20).mean()
        df["SMA_50"] = df["Close"].rolling(window=50).mean()
        
        # RSI
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df["Close"].ewm(span=12, adjust=False).mean()
        exp2 = df["Close"].ewm(span=26, adjust=False).mean()
        df["MACD"] = exp1 - exp2
        df["Signal_Line"] = df["MACD"].ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        df["BB_middle"] = df["Close"].rolling(window=20).mean()
        df["BB_upper"] = df["BB_middle"] + 2 * df["Close"].rolling(window=20).std()
        df["BB_lower"] = df["BB_middle"] - 2 * df["Close"].rolling(window=20).std()
        
        return df
    
    def _save_model(self, model: nn.Module, model_type: str,
                   symbol: str) -> str:
        """Save trained model to disk."""
        model_path = os.path.join(
            self.model_dir,
            f"{model_type}_{symbol}_{datetime.now().strftime('%Y%m%d')}.pth"
        )
        
        torch.save(model.state_dict(), model_path)
        return model_path
    
    def _load_model(self, model_type: str, symbol: str) -> Optional[nn.Module]:
        """Load trained model from disk."""
        try:
            model_files = [f for f in os.listdir(self.model_dir)
                          if f.startswith(f"{model_type}_{symbol}")]
            if not model_files:
                return None
            
            # Get most recent model
            latest_model = sorted(model_files)[-1]
            model_path = os.path.join(self.model_dir, latest_model)
            
            # Initialize model architecture
            model = self._initialize_model(model_type)
            
            # Load weights
            model.load_state_dict(torch.load(model_path))
            model.to(self.device)
            model.eval()
            
            return model
        except Exception:
            return None
    
    def _generate_hyperparameters(self, trial: optuna.Trial,
                                model_type: str) -> Dict:
        """Generate hyperparameters for model optimization."""
        if model_type == "price_prediction":
            return {
                "input_size": trial.suggest_int("input_size", 5, 20),
                "hidden_size": trial.suggest_int("hidden_size", 32, 256),
                "num_layers": trial.suggest_int("num_layers", 1, 4)
            }
        elif model_type == "portfolio_optimization":
            return {
                "input_size": trial.suggest_int("input_size", 5, 20),
                "hidden_size": trial.suggest_int("hidden_size", 32, 256),
                "num_assets": trial.suggest_int("num_assets", 5, 20)
            }
        return {}
    
    async def _evaluate_model_performance(self, model: nn.Module,
                                        model_type: str,
                                        test_data: pd.DataFrame) -> Dict:
        """Evaluate model performance metrics."""
        try:
            model.eval()
            metrics = {}
            
            if model_type == "price_prediction":
                predictions = model(torch.tensor(test_data.values).float())
                actuals = torch.tensor(test_data["Close"].values).float()
                
                # Calculate metrics
                mse = nn.MSELoss()(predictions, actuals)
                mae = nn.L1Loss()(predictions, actuals)
                
                metrics.update({
                    "mse": mse.item(),
                    "mae": mae.item(),
                    "rmse": np.sqrt(mse.item())
                })
            
            elif model_type == "sentiment_analysis":
                # Calculate sentiment metrics
                pass
            
            elif model_type == "portfolio_optimization":
                # Calculate portfolio metrics
                pass
            
            return metrics
        except Exception:
            return {}
    
    def _calculate_prediction_confidence(self,
                                      predictions: Union[pd.Series, pd.DataFrame]) -> float:
        """Calculate confidence score for predictions."""
        try:
            if isinstance(predictions, pd.Series):
                # For price predictions
                return 1 - predictions.std() / predictions.mean()
            elif isinstance(predictions, pd.DataFrame):
                # For portfolio weights
                return 1 - predictions.std().mean()
            return 0.5
        except Exception:
            return 0.5
