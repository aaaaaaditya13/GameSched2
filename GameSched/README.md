# GameSched - CPU Scheduling Visualizer

A web-based game that demonstrates how CPU scheduling algorithms affect real-time performance through an interactive challenge.

## Quick Start

```bash
python run_web.py       # Auto-installs dependencies and opens browser
```

## Game Objective

**Goal**: Move your green player from START to FINISH line while AI enemies (red circles) try to block your path.

## Controls

- **WASD** or **Arrow Keys** - Move player
- **SPACE** - Play/Pause
- **S** - Switch scheduling algorithm
- **R** - Reset game
- **ESC** - Exit

## Scheduling Algorithms

### FCFS (First Come First Serve)
- **Difficulty**: Hardest - unpredictable lag spikes
- **Effect**: Player may freeze when enemies queue first (convoy effect)
- **Learning**: Shows why FCFS is poor for interactive systems

### Round Robin
- **Difficulty**: Medium - predictable delays
- **Effect**: Fair time sharing, consistent but delayed responses
- **Learning**: Balanced approach to process scheduling

### Priority (Non-Preemptive)
- **Difficulty**: Easier - player advantage
- **Effect**: Player gets priority but can't interrupt running processes
- **Learning**: Priority-based resource allocation

### Priority (Preemptive)
- **Difficulty**: Easiest - optimal for gaming
- **Effect**: Best responsiveness, player can interrupt enemies
- **Learning**: Real-time system scheduling approach

## Visual Feedback

- **Green Rings**: Entity is responsive (low delay <100ms)
- **Yellow Rings**: Entity has medium delay (100-300ms)
- **Red Rings**: Entity is blocked/high delay (>300ms)
- **Process Queue**: Shows active threads waiting to execute

## Installation

### Requirements
- Python 3.7+
- 4GB RAM minimum

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install flask flask-socketio python-socketio
```

### Run the Application
```bash
python run_web.py
```
Opens browser at http://localhost:5000

## Project Structure

```
GameSched/
├── run_web.py              # Application entry point
├── web_game_engine.py      # Game engine with scheduling logic
├── web_server.py           # Flask server with WebSocket support
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates
│   ├── index.html         # Main game interface
│   ├── analytics.html     # Performance dashboard
│   └── tutorial.html      # Educational tutorial
└── static/                 # JavaScript files
    ├── game.js            # Game rendering and controls
    └── analytics.js       # Analytics visualization
```

## Learning Objectives

- Experience how scheduling algorithms affect real-time applications
- Understand trade-offs between fairness and responsiveness
- See why priority scheduling is crucial for interactive systems
- Learn about process queuing and resource contention
- Visualize convoy effect and starvation problems

## Game Strategy

1. **With FCFS**: Move quickly during gaps when enemies are delayed
2. **With Round Robin**: Use consistent timing to predict enemy movements
3. **With Priority**: Take advantage of your high-priority status
4. **Compare Times**: See which algorithm helps you finish fastest!

## Features

### Phase 1: Core Setup ✅
- ✓ Python + Pygame/Flask implementation
- ✓ Thread/Process class simulation
- ✓ FCFS scheduler with game loop
- ✓ Queue overlay visualization

### Phase 2: Gameplay and Algorithms ✅
- ✓ All 4 algorithms (FCFS, RR, Priority, Priority-Preemptive)
- ✓ Gameplay affected by scheduling delays
- ✓ Runtime algorithm switching
- ✓ Enhanced queue visualization
- ✓ Goal/challenge logic

### Phase 3: Metrics and Polish ✅
- ✓ Performance metrics (waiting time, FPS, throughput)
- ✓ Enhanced visuals and UI
- ✓ Web interface with analytics
- ✓ Documentation
- ✓ Tutorial system

## Performance Metrics

The game tracks and displays:
- **Waiting Time**: Time process spends in ready queue
- **Turnaround Time**: Total time from arrival to completion
- **Response Time**: Time from arrival to first execution
- **Throughput**: Processes completed per second
- **Context Switches**: Number of process switches
- **FPS**: Frames per second (target: 30 FPS)

## Web Interface Features

- Real-time game rendering on HTML5 Canvas
- Interactive algorithm selection
- Process speed control slider
- Live performance charts (Chart.js)
- Analytics dashboard with comparisons
- Tutorial system with step-by-step guide
- Responsive design (Tailwind CSS)

## API Documentation

### WebSocket Events

**Client to Server:**
- `start_game` - Initialize game loop
- `pause_game` - Toggle pause
- `reset_game` - Reset game and metrics
- `switch_scheduler` - Cycle algorithms
- `select_algorithm` - Choose specific algorithm
- `set_speed` - Adjust process creation rate
- `player_move` - Send movement input
- `request_metrics` - Get performance data

**Server to Client:**
- `game_update` - Real-time game state
- `metrics_update` - Performance analytics

### REST Endpoints
- `GET /` - Main game interface
- `GET /analytics` - Performance dashboard
- `GET /tutorial` - Educational tutorial

## Troubleshooting

### Application won't start
```bash
pip install --upgrade flask flask-socketio python-socketio
```

### Port 5000 in use
Change port in `web_server.py` line: `socketio.run(app, port=5000)`

### Slow performance
- Reduce process creation speed (web version slider)
- Close other applications
- Limit concurrent processes to 50

## Educational Use

### Classroom Integration
- Interactive demonstrations of scheduling concepts
- Student experiments with different scenarios
- Performance analysis with quantitative metrics
- Visual learning with real-time feedback

### Learning Outcomes
Students will understand:
1. How scheduling algorithms work in practice
2. Trade-offs between different approaches
3. Impact on real-time system performance
4. Process states and transitions
5. Context switching overhead

## Technical Specifications

- **Target FPS**: 30 FPS game loop
- **Metrics Update**: Every 1 second
- **Max Processes**: 100 concurrent
- **UI Response**: <100ms interaction delay
- **Browser Support**: Chrome, Firefox, Edge (HTML5 Canvas)

## Dependencies

- `flask==2.3.3` - Web framework
- `flask-socketio==5.3.6` - Real-time communication
- `python-socketio==5.8.0` - WebSocket support

## Contributing

1. Fork repository
2. Create feature branch
3. Implement changes with tests
4. Follow PEP 8 style guide
5. Add docstrings and comments
6. Submit pull request

## License

Educational use for computer science curricula, particularly Operating Systems and Systems Programming courses.

## Acknowledgments

- Chart.js for visualization
- Tailwind CSS for UI design
- Flask and Socket.IO communities
- Educational institutions for feedback

---

**Status**: ✅ Production Ready | **Version**: Web-Only
