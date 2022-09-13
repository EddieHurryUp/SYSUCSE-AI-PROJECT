import numpy as np
import copy
from queue import PriorityQueue
import heapq
target = {}
num = 1
for i in range(4):
	for j in range(4):
		target[num] = (i, j)
		num += 1
		
target[0] = (3, 3)
goal = str([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]])
class node:
    def __init__(self,list,depth,parent):
        self.depth  = depth
        self.state = list
        self.f = self.depth + self.h()
        self.hash_val = hash(str(self.state))
        self.parent = parent

    def h1(self):
        return self.h() - self.depth

    def h2(self):
        cost = 0
        if(self.state):
            for i in range(4):
                for j in range(4):
                    num = self.state[i][j]
                    (x,y) = target[num]
                    if(x!=i or y != j):
                        cost = cost + 1
        return cost

    def h(self):
        cost = 0
        if(self.state):
            for i in range(4):
                for j in range(4):
                        num = self.state[i][j]
                        if num != 0:
                            x, y = target[num]
                            cost += abs(x-i) + abs(y-j)
        return cost

    def __lt__(self, other):
        if self.f ==  other.f:
            return -self.depth < -other.depth 
        return self.f < other.f

    def get_state(self):
        return self.state

    def get_depth(self):
        return self.depth

    def __eq__(self, another):
        return self.hash_val == another.hash_val

def find_zero(list):
    for i in range(4):
        for j in range(4):
            if(list[i][j] == 0):
                return (i,j)

def expand(open,open_hashtable,close_hashtable,dic):
    tar = open.get()
    list1 = tar.get_state()
    close_hashtable.add(hash(str(list1)))
    moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    zero_position = find_zero(list1)
    x = zero_position[0]
    y = zero_position[1]
    for i, j in moves:
        a, b = x+i, y+j
        if(a<4 and a>-1 and b<4 and b>-1):
            list2 = copy.deepcopy(list1)
            list2[x][y] = list2[a][b]
            list2[a][b] = 0
            depth_now = tar.get_depth()
            newnode = node(list2,depth_now+1,tar)
            if is_goal(list2):
                print("game finished! The process is:")
                print_result(newnode)
                return 1,tar 
            if not(newnode.hash_val in close_hashtable):
                if not(newnode.hash_val in open_hashtable):
                    open.put(newnode)
                    dic[newnode.hash_val] = newnode
                    open_hashtable.add(newnode.hash_val)
                else:
                    if dic[newnode.hash_val].f > newnode.f:
                        dic[newnode.hash_val].f = newnode.f
                        dic[newnode.hash_val].parent = tar
                        dic[newnode.hash_val].depth = tar.depth+1
    return 0
def is_goal(list):
	return str(list) == goal

def print_result(node):
    depth = node.depth
    nodes = []
    while (node.depth != 0):
        nodes.append(node.state)
        node = node.parent
    for i in range(len(nodes)-1, -1,-1):
        print(np.array(nodes[i]))
        print('-------------------')
    # f.close()
    print("Depth:", depth)

def main():
    import time
    start = time.time()
    dic = dict()
    state =[[14,2,8,1], [7,10,4,0], [6,15,11,5], [9,3,13,12]]
    open = PriorityQueue()
    first_node = node(state,0,node([],0,""))
    dic[first_node.hash_val] = first_node
    open.put(first_node)
    open_hashset = set()
    open_hashset.add(first_node.hash_val)
    close_hashset = set()
    result = 0
    times = 0
    while(result == 0):
        result = expand(open,open_hashset,close_hashset,dic)
        times = times + 1
    end = time.time()
    print(end-start)

if __name__ == '__main__':
    main()


