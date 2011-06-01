from django.shortcuts import render_to_response
from django.utils import simplejson

def start_game(request):
	request.session['game_state'] = 'start'
	request.session['game_board'] = '000000000'
	
	return render_to_response('board.html')
	
def pick_order(request, play_order):
	data = {}
	game_state = request.session['game_state']
	game_board = request.session['game_board']
	if game_state == 'start':
		if play_order == 2:
			board = Board(game_board)
			new_board, computer_move = turn(board, 'X')
			request.session['game_board'] = new_board.board_state
			data.update({'computer_move':computer_move})
		elif play_order != 1:
			data.update({'message':'invalid command'})
		request.session['game_state'] = 'wait'
		
		data.update({'message':'game_started'})
	return HttpResponse(simplejson.dumps(data), mimetype = 'application/json')
	
def make_move(request, move):
	game_state = request.session['game_state']
	game_board = request.session['game_board']
	data = {}
	if game_state == 'wait':
		board = Board(game_board)
		board.update_state(move, 'O')
		game_board = board.board_state
		request.session['game_board'] = game_board
		
		new_board, computer_move = turn(board, 'X')
		if new_board.game_over():
			data.update({'message':'game_over'})
			if new_board.winner():
				data.update({'winner':new_board.winner()})
		else:
			data.update({'message':'game_started'})
		data.update({'computer_move':computer_move})
		
	return HttpResponse(simplejson.dumps(data), mimetype = 'application/json')
				

def turn(board, player):
	opponent = {computer:human, human:computer}
		
	def judge(winner):
		"""judge whether or not the player has won the match"""
		if not winner:
			return 0
		if winner == player:
			return +1
		return -1
		
		
	def evaluate_move(move, p=player):
		"""evaluate the outcome of a particular move"""
		try:
			board.execute_move(move, p)
			if board.game_over():
				return judge(board.winner())
			valid_moves = board.get_valid_moves()
			
			outcomes = (evaluate_move(next_move, opponent[p]) for next_move in valid_moves)
			if p == player:
				min_element = 1
				for o in outcomes:
					if o == -1:
						return o
					min_element = min(o,min_element)
				return min_element
			else:
				max_element = -1
				for o in outcomes:
					if o == +1:
						return o
					max_element = max(o,max_element)
				return max_element
			
		finally:
			board.reverse_move(move)
			
	moves = [(move, evaluate_move(move)) for move in board.get_valid_moves()]
	random.shuffle(moves)
	moves.sort(key = lambda (move, winner): winner)
	import ipdb; ipdb.set_trace()