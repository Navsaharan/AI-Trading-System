# FamilyHVSDN Trading System

An advanced Indian trading system that combines real-time market data with AI-powered predictions for automated trading.

## Features

### Trading Features
- Real-time market data from NSE/BSE
- Technical indicators (SMA, RSI, MACD)
- Volume analysis
- Market depth
- Auto-trading capabilities
- Risk management system

### AI Features
- Price predictions using LSTM
- Sentiment analysis of news
- Market regime detection
- Risk analysis
- Portfolio optimization

### User Features
- Portfolio tracking
- Real-time alerts
- Custom watchlists
- Performance analytics
- Mobile-responsive interface

### Admin Features
- User management
- System monitoring
- Risk management
- Performance tracking
- API key management

## Quick Start

1. **Install Dependencies**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

3. **Start the System**
```bash
# Start the trading system
python start.py
```

## Documentation

- [Complete Setup Guide](COMPLETE_SETUP.md) - Detailed installation and setup
- [Auto Trading Guide](AUTO_TRADING_AND_AUTH.md) - Auto trading setup and authentication
- [API Documentation](docs/API.md) - API endpoints and usage
- [User Guide](docs/USER_GUIDE.md) - Guide for regular users
- [Admin Guide](docs/ADMIN_GUIDE.md) - Guide for administrators

## System Architecture

```
Frontend (React) ←→ Backend (Python/Flask) ←→ Trading Engine
     ↑                      ↑                       ↑
     ↓                      ↓                       ↓
  UI/UX Layer        API/Auth Layer          Trading Layer
     ↑                      ↑                       ↑
     ↓                      ↓                       ↓
User Interface    Data Processing         Market Connection
```

## Safety Features

1. **Risk Management**
   - Maximum daily loss limit (2%)
   - Position size limits
   - Correlation checks
   - Emergency stop system

2. **Monitoring**
   - Real-time performance tracking
   - Automated alerts
   - System health checks
   - Error detection

3. **Security**
   - Firebase authentication
   - API key management
   - Role-based access
   - Audit logging

## Development

1. **Setup Development Environment**
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest
```

2. **Code Style**
```bash
# Check code style
flake8 src/

# Format code
black src/
```

## Deployment

1. **Server Requirements**
   - Ubuntu 20.04 or higher
   - Python 3.8+
   - PostgreSQL
   - Redis
   - Nginx

2. **Deployment Steps**
```bash
# Clone repository
git clone https://github.com/yourusername/familyhvsdn.git

# Setup environment
cd familyhvsdn
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your credentials

# Start services
sudo systemctl start postgresql
sudo systemctl start redis
sudo systemctl start nginx

# Start application
python start.py
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

- Technical Support: support@your-domain.com
- Trading Support: trading@your-domain.com
- Emergency: emergency@your-domain.com

## License

This project is proprietary software. All rights reserved.
