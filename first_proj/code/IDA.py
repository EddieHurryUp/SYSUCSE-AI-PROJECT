import numpy as np
goal = str([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]])
target = {}
def build_target():
	num = 1
	for i in range(4):
		for j in range(4):
			target[num] = (i, j)
			num += 1
	target[0] = (3, 3)
 
def h(node):
	cost = 0
	for i in range(4):
		for j in range(4):
			num = node[i][j]
			if(num != 0):
				x, y = target[num]
				cost += abs(x-i) + abs(y-j)
	return cost

def main_funct(state,limit):
	bound = h(state)
	path = [state]
	while(True):
		tar = dfs(path, 0, bound)
		if(tar == -1):
			return (path, bound)
		if(tar > limit):
			return ([], bound)
		bound = tar

def frontier(node):
	x, y = 0, 0
	for i in range(4):
		for j in range(4):
			if(node[i][j] == 0):
				x, y = i, j
	frontier = []
	moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
	for i, j in moves:
		a, b = x+i, y+j
		if(a<4 and a>-1 and b<4 and b>-1):
			temp = [[num for num in col] for col in node]
			temp[x][y] = temp[a][b]
			temp[a][b] = 0
			frontier.append(temp)
			
	return sorted(frontier, key=lambda x: h(x))
	
def is_goal(node):
	return str(node) == goal
		
def dfs(path, g, bound):
	node = path[-1]
	f = g + h(node)
	if(f > bound):
		return f
	if(is_goal(node)):
		return -1
	m = 9999
	for ir in frontier(node):
		if ir not in path:
			path.append(ir)
			t = dfs(path, g+1, bound)
			if(t == -1):
				return -1
			if(t < m):
				m = t
			path.pop()
			# print("pop!")
			
	return m
 
		
def main():
	build_target()
	state =  [[14,2,8,1], [7,10,4,0], [6,15,11,5], [9,3,13,12]]
	import time
	start = time.time()	
	limit =  50
	(path, bound) = main_funct(state,limit)
	end = time.time()
	step = 0
	for p in path:
		print('step', step)
		step += 1
		for row in p:
			print(row)

	print('bound', bound)
	print('time',end-start)

if __name__ == '__main__':
    main() 