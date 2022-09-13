from operator import ge
import numpy as np
import random
import matplotlib.pyplot as plt
import copy
import heapq
import mutation
coordinate_x = []
coordinate_y = []
x = []
y = []
def read_data(filename):
    f = open(filename,'r')
    lines = f.readlines()
    for line in lines:
        data = line.split()
        coordinate_x.append(float(data[1]))
        coordinate_y.append(float(data[2]))

read_data("ch150.txt")

class Individual:
    def __init__(self,state,problem_size):
        self.problem_size = problem_size
        self.state = state
        self.score = 0
        for i in range(self.problem_size - 1):
            self.score += self.get_distance(self.state[i] , self.state[i+1])
        self.score += self.get_distance(self.state[0] , self.state[-1])
        self.score = 100000 - self.score

    def __lt__(self,another):
        return self.score > another.score

    def get_distance(self, point_a , point_b):
        tmp1 = pow((coordinate_x[point_a] - coordinate_x[point_b]),2)    
        tmp2 = pow((coordinate_y[point_a] - coordinate_y[point_b]),2)
        tmp = tmp1 + tmp2
        return pow(tmp,0.5)
    
    def mutation(self,mutation_p):
        if np.random.rand() < mutation_p:
            new_state = mutation.inversion_mutation(self.state)
            new_score = 0
            for i in range(self.problem_size - 1):
                new_score += self.get_distance(new_state[i] , new_state[i+1])
            new_score = 100000 - new_score
            
            self.score = new_score
            self.state = new_state    

class genetic_algorithm:
    def __init__(self,problem_size,max_population):
        self.problem_size = problem_size
        self.max_population = max_population
        self.population = []
        tmp_population_size = 0
        while tmp_population_size < self.max_population:
            rand_state = self.genarate_random_list(problem_size)
            tmp_population_size += 1
            new_ind = Individual(rand_state,self.problem_size)
            self.population.append(new_ind)
            tmp = []
            for v in self.population:
                heapq.heappush(tmp,v)
            self.population = [heapq.heappop(tmp) for i in range(len(tmp))]
            # print("-------------------------")
            # for i in self.population:
            #     print(i.score)
            # print("-------------------------")
    
    def genarate_random_list(self,point_num):
        point_list = [0]*(point_num-1)
        for i in range(0,point_num-1):
            point_list[i] = i + 1
        random.shuffle(point_list)
        point_list.insert(0,0)
        point_list.append(0)
        return point_list


    def get_two_parents(self):
        remained_population = self.population
        parent1 = -1
        parent2 = -1
        total_score = self.get_total_score()
        size = len(remained_population)
        while parent1 == parent2:
            roulette1 = random.uniform(0,total_score)
            for i in range(size):
                roulette1 -= self.population[i].score
                if roulette1 < 0:
                    parent1 = i
                    break

            roulette2 = random.uniform(0,total_score)
            for j in range(size):
                roulette2 -= self.population[j].score
                if roulette2 < 0:
                    parent2 = j
                    break
        # print(parent1,parent2)
        return parent1,parent2

    def get_total_score(self):
        remained_population = self.population
        totals_score = 0
        for i in remained_population:
            totals_score += i.score
        return totals_score

    def get_children(self):
        parent1,parent2 = self.get_two_parents()
        new_child1,new_child2 = self.crossover2(parent1,parent2)
        new_child1.mutation(0.25)
        new_child2.mutation(0.25)
        return new_child1,new_child2
    
    def get_next_genaration(self):
        new_population = []
        new_population_size = 0
        while(new_population_size < self.max_population*0.3):
            new_population.append(self.population[new_population_size])
            new_population_size += 1
        while(len(new_population) < self.max_population):
            new_c1,new_c2 = self.get_children()
            if new_c1 not in new_population:
                new_population.append(new_c1)
            if new_c2 not in new_population:
                new_population.append(new_c2)
        tmp = []
        for v in new_population:
            heapq.heappush(tmp,v)
        new_population = [heapq.heappop(tmp) for i in range(len(tmp))]
        self.population = new_population
    
    def crossover2(self,parent1,parent2):
        ord1 = random.randint(0, self.problem_size)
        ord2 = random.randint(0, self.problem_size)
        son1 = self.ox(parent1, parent2, ord1, ord2)
        son2 = self.ox(parent1, parent2, ord2, ord1)
        return son1,son2

    def ox(self,parent1, parent2, ord1, ord2):  # 顺序交叉
        son1 = self.population[parent1].state[ord1:ord2]
        son2 = []
        for gene in  self.population[parent2].state:
            if gene not in son1:
                son2.append(gene)  # 继承父代2
        for i in range(len(son1)):  # 插入
            son2.insert(ord1, son1[len(son1) - i - 1])
        return Individual(son2,self.problem_size)

    def show(self,title,genaration):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set(xlim=[0,800 ], ylim=[0, 800], title=title ,
        ylabel='Y-Axis', xlabel='X-Axis')
        x = []
        y = []
        for i in self.population[0].state:
            tmp_x = coordinate_x[i]
            tmp_y = coordinate_y[i]
            x.append(tmp_x)
            y.append(tmp_y)
        x.append(coordinate_x[self.population[0].state[0]])
        y.append(coordinate_y[self.population[0].state[0]])
        ax.plot(x, y)
        plt.savefig("./res2/" + str(genaration) + "." + "jpg")
        # plt.show()

    def show2(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set(xlim=[0,25000], ylim=[0, 60000], title = "G-SCORE" ,
        ylabel='Y-Axis', xlabel='X-Axis')
        ax.plot(x, y)
        plt.savefig("./res2/end.jpg")
        # plt.show() 

    def solve(self):
        self.show("start","0")
        genaration = 0
        while genaration < 30000:
            title = ""
            if genaration%1000 == 0:
                x.append(genaration)
                y.append(100000 - self.population[0].score)
                title = str(genaration) + " : " + str(100000 - self.population[0].score)
                self.show(title,genaration)
            genaration += 1
            self.get_next_genaration()
            print(self.population[0].score)
        self.show2()

problem = genetic_algorithm(150,25)
problem.solve()