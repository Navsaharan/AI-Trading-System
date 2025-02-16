from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from ..database.models import User, Strategy, Trade, Position, BrokerAPIKey
from ..core.trading_engine import TradingEngine
from ..brokers.binance import BinanceBroker
from ..models.sentiment_model import SentimentModel

# Initialize FastAPI app
app = FastAPI(
    title="FamilyHVSDN Trading System API",
    description="Advanced Indian trading system with AI-powered predictions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class StrategyCreate(BaseModel):
    name: str
    description: str
    type: str
    parameters: Dict

class BrokerAPIKeyCreate(BaseModel):
    broker_name: str
    api_key: str
    api_secret: str

# Dependencies
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Auth routes
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                               db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# User routes
@app.post("/users/", response_model=dict)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully"}

# Strategy routes
@app.post("/strategies/", response_model=dict)
async def create_strategy(strategy: StrategyCreate,
                         current_user: User = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    db_strategy = Strategy(
        user_id=current_user.id,
        name=strategy.name,
        description=strategy.description,
        type=strategy.type,
        parameters=strategy.parameters
    )
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return {"message": "Strategy created successfully"}

@app.get("/strategies/", response_model=List[dict])
async def get_strategies(current_user: User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    strategies = db.query(Strategy).filter(Strategy.user_id == current_user.id).all()
    return [strategy.__dict__ for strategy in strategies]

# Broker API routes
@app.post("/broker-keys/", response_model=dict)
async def add_broker_api_key(api_key: BrokerAPIKeyCreate,
                            current_user: User = Depends(get_current_user),
                            db: Session = Depends(get_db)):
    db_api_key = BrokerAPIKey(
        user_id=current_user.id,
        broker_name=api_key.broker_name,
        api_key=api_key.api_key,
        api_secret=api_key.api_secret
    )
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    return {"message": "API key added successfully"}

# Trading routes
@app.post("/trading/start", response_model=dict)
async def start_trading(strategy_id: int,
                       current_user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Get broker API keys
    api_key = db.query(BrokerAPIKey).filter(
        BrokerAPIKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=400, detail="No broker API keys found")
    
    # Initialize broker
    broker = BinanceBroker(api_key.api_key, api_key.api_secret)
    
    # Initialize AI models
    sentiment_model = SentimentModel()
    await sentiment_model.train(None)  # Initialize pre-trained model
    
    ai_models = {
        'sentiment': sentiment_model
    }
    
    # Create and start trading engine
    engine = TradingEngine(current_user, broker, strategy, ai_models)
    success = await engine.start()
    
    if success:
        return {"message": "Trading started successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to start trading")

@app.get("/trading/positions", response_model=List[dict])
async def get_positions(current_user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    positions = db.query(Position).filter(Position.user_id == current_user.id).all()
    return [position.__dict__ for position in positions]

@app.get("/trading/trades", response_model=List[dict])
async def get_trades(current_user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    trades = db.query(Trade).filter(Trade.user_id == current_user.id).all()
    return [trade.__dict__ for trade in trades]

# Helper functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
