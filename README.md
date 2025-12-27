# antistress_maze
I want to create a video game that help to alleviate anxiety.

## Run gui instructions
`pip install -r requirements.txt`
`python breathing_meditation_gui_03.py`

# Breathing Meditation Web Application

A breathing meditation application with procedural maze exploration. Navigate through a dynamically generated maze while following guided breathing cycles.

## Architecture

This application uses an **object-oriented Python backend** with Flask handling all game logic:

### Backend (Python)
- **BreathingState**: Manages breathing cycles (inhale, hold, exhale)
- **Player**: Handles player position and movement validation
- **Maze**: Generates procedural mazes and calculates lighting/visibility
- **GameSession**: Orchestrates complete game sessions with state management

### Frontend (JavaScript)
- Minimal client-side logic - only handles:
  - Canvas rendering of data from backend
  - Keyboard input capture
  - API communication

## Features

- **Procedural Maze Generation**: Each session creates a unique 100x100 maze
- **Breathing Guidance**: Visual feedback through light radius and color changes
- **Dynamic Lighting**: Line-of-sight visibility with smooth falloff
- **Session Management**: Multiple concurrent users with automatic cleanup

## Local Development

### Prerequisites
- Python 3.11+
- pip

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser to `http://localhost:5000`

### Controls
- **WASD** or **Arrow Keys**: Move through the maze
- Follow the breathing phases indicated at the bottom:
  - **INHALE** (Cyan): Light expands
  - **HOLD** (Yellow): Light stays at maximum/minimum
  - **EXHALE** (Blue): Light contracts

## Deploying to Heroku

### Prerequisites
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed
- A Heroku account

### Deployment Steps

1. **Login to Heroku**:
```bash
heroku login
```

2. **Create a new Heroku app**:
```bash
heroku create your-app-name
```

3. **Deploy the application**:
```bash
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

4. **Open your application**:
```bash
heroku open
```

### Heroku Configuration

The application is configured for Heroku with:
- `Procfile`: Specifies the web process (gunicorn)
- `requirements.txt`: Python dependencies
- `runtime.txt`: Python version specification
- Port configuration from environment variable

### Monitoring

Check logs:
```bash
heroku logs --tail
```

View active sessions:
```bash
curl https://your-app-name.herokuapp.com/api/health
```

## API Endpoints

### POST `/api/session/create`
Create a new game session
- Returns: `{ session_id, config }`

### GET `/api/session/<session_id>/state`
Get current game state
- Returns: Complete state including breathing phase, player position, and visible cells

### POST `/api/session/<session_id>/move`
Move the player
- Body: `{ "direction": "up|down|left|right" }`
- Returns: `{ success, player }`

### GET `/api/config`
Get game configuration

### GET `/api/health`
Health check and session count

## Configuration

Edit `CONFIG` in `app.py` to adjust:
- `INHALE_TIME`: Duration of inhale phase (seconds)
- `HOLD_AFTER_INHALE`: Duration of hold after inhale (seconds)
- `EXHALE_TIME`: Duration of exhale phase (seconds)
- `HOLD_AFTER_EXHALE`: Duration of hold after exhale (seconds)
- `MIN_LIGHT_RADIUS`: Minimum visibility radius
- `MAX_LIGHT_RADIUS`: Maximum visibility radius
- `MAZE_SIZE`: Size of the generated maze (100x100 default)

## Performance

- Sessions automatically expire after 30 minutes of inactivity
- Only visible cells are rendered (optimized for large mazes)
- 30 FPS update rate for smooth breathing transitions

## License

MIT

# Mail
artem @ abalmasov.com