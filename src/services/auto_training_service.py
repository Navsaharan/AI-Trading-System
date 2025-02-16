from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import torch
import torch.nn as nn
from torch.cuda.amp import autocast, GradScaler
import tensorflow as tf
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from sklearn.model_selection import TimeSeriesSplit
import joblib
import os
import json
from concurrent.futures import ThreadPoolExecutor
import asyncio
import logging
from pathlib import Path

class AutoTrainingService:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.scaler = GradScaler()
        self.executor = ThreadPoolExecutor(max_workers=8)
        self.setup_logging()
        self.initialize_components()

    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "auto_training.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("AutoTraining")

    def initialize_components(self):
        """Initialize training components"""
        try:
            self.models_dir = Path("models")
            self.data_dir = Path("data")
            self.checkpoints_dir = Path("checkpoints")
            
            # Create directories
            for directory in [self.models_dir, self.data_dir, self.checkpoints_dir]:
                directory.mkdir(exist_ok=True)
            
            self.logger.info("Auto-training service initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing auto-training: {e}")

    async def start_auto_training(self):
        """Start automatic training process"""
        try:
            while True:
                self.logger.info("Starting auto-training cycle")
                
                # Fetch new data
                new_data = await self._fetch_new_data()
                if new_data is not None:
                    # Train models in parallel
                    await asyncio.gather(
                        self._train_market_predictor(new_data),
                        self._train_sentiment_analyzer(new_data),
                        self._train_portfolio_optimizer(new_data),
                        self._train_risk_analyzer(new_data)
                    )
                
                # Save checkpoints
                self._save_checkpoints()
                
                # Log performance metrics
                self._log_performance()
                
                # Wait for next training cycle
                await asyncio.sleep(3600)  # Train every hour
                
        except Exception as e:
            self.logger.error(f"Error in auto-training cycle: {e}")

    async def _fetch_new_data(self) -> Optional[Dict[str, pd.DataFrame]]:
        """Fetch new training data"""
        try:
            data = {}
            
            # Market data
            market_data = await self._fetch_market_data()
            if market_data is not None:
                data['market'] = market_data
            
            # News data for sentiment
            news_data = await self._fetch_news_data()
            if news_data is not None:
                data['news'] = news_data
            
            # Portfolio data
            portfolio_data = await self._fetch_portfolio_data()
            if portfolio_data is not None:
                data['portfolio'] = portfolio_data
            
            return data if data else None
            
        except Exception as e:
            self.logger.error(f"Error fetching new data: {e}")
            return None

    async def _train_market_predictor(self, data: Dict[str, pd.DataFrame]):
        """Train market prediction model"""
        try:
            market_data = data['market']
            
            # Prepare data
            X, y = self._prepare_market_data(market_data)
            
            # Split data
            tscv = TimeSeriesSplit(n_splits=5)
            
            for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
                X_train, X_val = X[train_idx], X[val_idx]
                y_train, y_val = y[train_idx], y[val_idx]
                
                # Convert to tensors
                X_train = torch.FloatTensor(X_train).to(self.device)
                y_train = torch.FloatTensor(y_train).to(self.device)
                X_val = torch.FloatTensor(X_val).to(self.device)
                y_val = torch.FloatTensor(y_val).to(self.device)
                
                # Train with mixed precision
                with autocast():
                    # Forward pass
                    y_pred = self.market_predictor(X_train)
                    loss = nn.MSELoss()(y_pred, y_train)
                
                # Backward pass
                self.scaler.scale(loss).backward()
                self.scaler.step(self.optimizer)
                self.scaler.update()
                
                # Validate
                with torch.no_grad():
                    val_pred = self.market_predictor(X_val)
                    val_loss = nn.MSELoss()(val_pred, y_val)
                
                self.logger.info(f"Fold {fold + 1} - Train Loss: {loss.item():.4f}, Val Loss: {val_loss.item():.4f}")
            
            # Save model
            self._save_model('market_predictor')
            
        except Exception as e:
            self.logger.error(f"Error training market predictor: {e}")

    async def _train_sentiment_analyzer(self, data: Dict[str, pd.DataFrame]):
        """Train sentiment analysis model"""
        try:
            news_data = data['news']
            
            # Prepare data
            texts, labels = self._prepare_sentiment_data(news_data)
            
            # Fine-tune model
            self.sentiment_model.train()
            
            for epoch in range(5):
                total_loss = 0
                for i in range(0, len(texts), self.batch_size):
                    batch_texts = texts[i:i + self.batch_size]
                    batch_labels = labels[i:i + self.batch_size]
                    
                    # Tokenize
                    inputs = self.tokenizer(
                        batch_texts,
                        padding=True,
                        truncation=True,
                        return_tensors="pt"
                    ).to(self.device)
                    
                    # Forward pass
                    with autocast():
                        outputs = self.sentiment_model(**inputs, labels=batch_labels)
                        loss = outputs.loss
                    
                    # Backward pass
                    self.scaler.scale(loss).backward()
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                    
                    total_loss += loss.item()
                
                avg_loss = total_loss / (len(texts) / self.batch_size)
                self.logger.info(f"Epoch {epoch + 1} - Avg Loss: {avg_loss:.4f}")
            
            # Save model
            self._save_model('sentiment_analyzer')
            
        except Exception as e:
            self.logger.error(f"Error training sentiment analyzer: {e}")

    async def _train_portfolio_optimizer(self, data: Dict[str, pd.DataFrame]):
        """Train portfolio optimization model"""
        try:
            portfolio_data = data['portfolio']
            
            # Prepare data
            X, y = self._prepare_portfolio_data(portfolio_data)
            
            # Train model
            self.portfolio_optimizer.fit(X, y)
            
            # Save model
            self._save_model('portfolio_optimizer')
            
        except Exception as e:
            self.logger.error(f"Error training portfolio optimizer: {e}")

    async def _train_risk_analyzer(self, data: Dict[str, pd.DataFrame]):
        """Train risk analysis model"""
        try:
            market_data = data['market']
            
            # Prepare data
            X, y = self._prepare_risk_data(market_data)
            
            # Train model
            self.risk_analyzer.fit(X, y)
            
            # Save model
            self._save_model('risk_analyzer')
            
        except Exception as e:
            self.logger.error(f"Error training risk analyzer: {e}")

    def _save_model(self, model_name: str):
        """Save trained model"""
        try:
            model_path = self.models_dir / f"{model_name}.pth"
            
            if model_name == 'market_predictor':
                torch.save(self.market_predictor.state_dict(), model_path)
            elif model_name == 'sentiment_analyzer':
                self.sentiment_model.save_pretrained(self.models_dir / "sentiment")
            else:
                joblib.dump(
                    getattr(self, model_name),
                    self.models_dir / f"{model_name}.joblib"
                )
            
            self.logger.info(f"Saved {model_name} model")
            
        except Exception as e:
            self.logger.error(f"Error saving {model_name}: {e}")

    def _save_checkpoints(self):
        """Save training checkpoints"""
        try:
            checkpoint = {
                'market_predictor': self.market_predictor.state_dict(),
                'optimizer': self.optimizer.state_dict(),
                'scaler': self.scaler.state_dict(),
                'timestamp': datetime.now().isoformat()
            }
            
            checkpoint_path = self.checkpoints_dir / f"checkpoint_{datetime.now():%Y%m%d_%H%M}.pt"
            torch.save(checkpoint, checkpoint_path)
            
            self.logger.info("Saved training checkpoint")
            
        except Exception as e:
            self.logger.error(f"Error saving checkpoint: {e}")

    def _log_performance(self):
        """Log model performance metrics"""
        try:
            metrics = {
                'market_predictor': self._evaluate_market_predictor(),
                'sentiment_analyzer': self._evaluate_sentiment_analyzer(),
                'portfolio_optimizer': self._evaluate_portfolio_optimizer(),
                'risk_analyzer': self._evaluate_risk_analyzer()
            }
            
            # Save metrics
            metrics_path = Path("logs") / f"metrics_{datetime.now():%Y%m%d}.json"
            with open(metrics_path, 'w') as f:
                json.dump(metrics, f, indent=4)
            
            self.logger.info("Logged performance metrics")
            
        except Exception as e:
            self.logger.error(f"Error logging performance: {e}")

# Initialize auto-training service
auto_trainer = AutoTrainingService()
