from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time
from web_game_engine import WebLineCrossingGame

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cpu_scheduling_game'
socketio = SocketIO(app, cors_allowed_origins="*")

class WebGameController:
    def __init__(self):
        self.game = WebLineCrossingGame()
        self.running = False
        self.paused = False
        self.game_thread = None
        
    def start_game_loop(self):
        self.running = True
        while self.running:
            if not self.paused:
                dt = 1/30
                self.game.update(dt)
                game_state = self.game.get_state()
                socketio.emit('game_update', game_state)
            time.sleep(1/30)

game_controller = WebGameController()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')



@socketio.on('connect')
def handle_connect():
    # Reset game on new connection
    game_controller.game = WebLineCrossingGame()
    game_controller.running = False
    game_controller.paused = False
    print("Client connected, sending initial game state")
    emit('game_update', game_controller.game.get_state())

@socketio.on('start_game')
def handle_start_game():
    if not game_controller.running:
        game_controller.game_thread = threading.Thread(target=game_controller.start_game_loop)
        game_controller.game_thread.daemon = True
        game_controller.game_thread.start()

@socketio.on('pause_game')
def handle_pause_game():
    game_controller.paused = not game_controller.paused

@socketio.on('reset_game')
def handle_reset_game():
    game_controller.game.reset_game()

@socketio.on('switch_scheduler')
def handle_switch_scheduler():
    game_controller.game.scheduler.switch_scheduler()

@socketio.on('select_algorithm')
def handle_select_algorithm(data):
    game_controller.game.scheduler.select_algorithm(data['index'])

@socketio.on('set_speed')
def handle_set_speed(data):
    game_controller.game.set_process_speed(data['speed'])

@socketio.on('player_move')
def handle_player_move(data):
    dx, dy = data['dx'], data['dy']
    game_controller.game.move_player(dx, dy)

@socketio.on('request_metrics')
def handle_request_metrics():
    metrics_data = {
        'comparison': game_controller.game.scheduler.algorithm_metrics,
        'total_processes': len(game_controller.game.scheduler.completed_processes),
        'context_switches': game_controller.game.scheduler.context_switches,
        'fps_stats': {'average': 30.0},
        'fps_history': [30] * 60,
        'algorithm_stats': game_controller.game.scheduler.algorithm_metrics,
        'gantt_data': []
    }
    emit('metrics_update', metrics_data)



if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
