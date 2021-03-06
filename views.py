from django.shortcuts import render_to_response, HttpResponse
from django.utils import simplejson
from models import *
import sys

def start_game(request):
	# when the page loads set session variables to their initial state
	request.session['game_state'] = 'start'
	request.session['game_board'] = '000000000'
	
	return render_to_response('board.html')
	
def pick_order(request, play_order):
	#after the page has loaded, the player choses who goes first
	data = {}
	game_state = request.session['game_state']
	game_board = request.session['game_board']
	if game_state == 'start':
		if play_order == '2':
			# if the player picks the computer to go first, a move is made and a json response sent back
			board = Board(game_board)
			new_board, computer_move = turn(board, '2')
			request.session['game_board'] = new_board.board_state
			data.update({'computer_move':computer_move})
		elif play_order != '1':
			data.update({'message':'invalid_command'})
		request.session['game_state'] = 'wait'
		
		data.update({'message':'game_started'})
	return HttpResponse(simplejson.dumps(data), mimetype = 'application/json')
	
def make_move(request, move):
	# exeute the human player's move, then compute the computer's move and send back the results.
	game_state = request.session['game_state']
	game_board = request.session['game_board']
	data = {}
	if game_state == 'wait':
		data.update({'message':'game_started'})
		board = Board(game_board)
		if not int(move) in board.get_valid_moves():
			data.update({'message':'invalid_move'})
			return HttpResponse(simplejson.dumps(data), mimetype = 'application/json')
		board.update_state(move, '1')
		game_board = board.board_state
		request.session['game_board'] = game_board
		if board.game_over():
			data.update({'message':'game_over'})
			if board.winner():
				data.update({'winner':board.winner()})
		else:
			new_board, computer_move = turn(board, '2')
			if new_board.game_over():
				data.update({'message':'game_over'})
				if new_board.winner():
					data.update({'winner':new_board.winner()})
			request.session['game_board'] = new_board.board_state
			data.update({'computer_move':computer_move})
			
	return HttpResponse(simplejson.dumps(data), mimetype = 'application/json')
				

def turn(board, player):
	"""the minimax ai function"""
	opponent = {computer:human, human:computer}
		
	def judge(winner):
		"""judge whether or not the player has won the match"""
		if not winner:
			return 0
		if winner == player:
			return +10
		return -1
		
		
	def evaluate_move(move, p=player):
		"""evaluate all the outcome of a particular move recursively"""
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
					min_element = min(o,min_element) #minimax logic
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
	moves.sort(key = lambda (move, winner): winner) # sort the moves by the highest outcome value
	computer_move = moves[-1][0] # chose the last move
	board.execute_move(computer_move, '2') # execute it
	return board, computer_move