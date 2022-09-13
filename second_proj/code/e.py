from operator import ge
import numpy as np
import random
import matplotlib.pyplot as plt
x = []
y = []
class Simulate_Anneal:
    def __init__(self,problem_size,filename,max_temperature):
        self.k = 1
        self.problem_size = problem_size
        self.point_list = self.genarate_random_list(self.problem_size)
        self.coordinate_x = []
        self.coordinate_y = []
        self.read_data(filename)
        self.coordinate_x.append(self.coordinate_x[0])
        self.coordinate_y.append(self.coordinate_y[0])
        self.path_count = 0
        for i in range(self.problem_size - 1):
            self.path_count += self.get_distance(self.point_list[i] , self.point_list[i+1] , self.coordinate_x , self.coordinate_y)
        self.temperature = max_temperature
        self.max_temperature = max_temperature

    def read_data(self,filename):
        f = open(filename,'r')
        lines = f.readlines()
        for line in lines:
            data = line.split()
            self.coordinate_x.append(float(data[1]))
            self.coordinate_y.append(float(data[2]))

    def genarate_random_list(self,point_num):
        point_list = [0]*(point_num-1)
        for i in range(0,point_num-1):
            point_list[i] = i + 1
        random.shuffle(point_list)
        point_list.insert(0,0)
        point_list.append(0)
        return point_list

    def get_distance(self, point_a , point_b , coordinate_x , coordinate_y):
        tmp1 = pow((coordinate_x[point_a] - coordinate_x[point_b]),2)    
        tmp2 = pow((coordinate_y[point_a] - coordinate_y[point_b]),2)
        tmp = tmp1 + tmp2
        return pow(tmp,0.5)    
    
    def show1(self,title,k):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set(xlim=[0,800], ylim=[0,800], title=title,
        ylabel='Y-Axis', xlabel='X-Axis')
        ax.plot(self.coordinate_x, self.coordinate_y)
        # plt.savefig("./res1/" + str(k) + "." + "jpg")

    def show2(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set(xlim=[0,8000], ylim=[0, 60000], title="K-SCORE",
        ylabel='score', xlabel='K-value')
        ax.plot(x, y)
        # plt.savefig("./res1/end.jpg")

    def solve(self):
        self.show1(title = "start", k = 0)
        x.append(0)
        y.append(self.path_count)
        while self.temperature >0.05:
            self.temperature = self.max_temperature / (1 + self.k)
            if self.k % 100 == 0:
                x.append(self.k)
                y.append(self.path_count)
            if self.k % 500 == 0:
                title  = "temperature = " + str(self.temperature) + " score = " + str(int(self.path_count))
                self.show1(title,self.k)
            for i in range(100):
                print("使用模拟退火 , 温度为" , self.temperature  , ", 第 " , i , " 轮.")
                print(self.path_count)
                new_cost,new_x,new_y = self.get_new_state()
                if new_cost < self.path_count:
                    self.accept(new_cost,new_x,new_y)
                else:
                    if np.random.rand() < np.exp(-(new_cost-self.path_count)/self.temperature):
                        self.accept(new_cost,new_x,new_y)
            self.k = self.k + 1
        self.show2()
    def get_new_state(self):
        new_x = self.coordinate_x.copy()
        new_y = self.coordinate_y.copy()
        if np.random.rand() > 0.5:
            while True:#产生两个不同的随机数
                loc1 = np.int(np.ceil(np.random.rand()*(self.problem_size-1)))
                loc2 = np.int(np.ceil(np.random.rand()*(self.problem_size-1)))
                if loc1 != loc2:
                    break
            new_x[loc1],new_x[loc2] = new_x[loc2],new_x[loc1]
            new_y[loc1],new_y[loc2] = new_y[loc2],new_y[loc1]
        else:
            while True:
                loc1 = np.int(np.ceil(np.random.rand()*(self.problem_size-1)))
                loc2 = np.int(np.ceil(np.random.rand()*(self.problem_size-1))) 
                loc3 = np.int(np.ceil(np.random.rand()*(self.problem_size-1)))

                if((loc1 != loc2)&(loc2 != loc3)&(loc1 != loc3)):
                    break

            # 下面的三个判断语句使得loc1<loc2<loc3
            if loc1 > loc2:
                loc1,loc2 = loc2,loc1
            if loc2 > loc3:
                loc2,loc3 = loc3,loc2
            if loc1 > loc2:
                loc1,loc2 = loc2,loc1

            #下面的三行代码将[loc1,loc2)区间的数据插入到loc3之后
            tmplist = new_x[loc1:loc2].copy()
            new_x[loc1:loc3-loc2+1+loc1] = new_x[loc2:loc3+1].copy()
            new_x[loc3-loc2+1+loc1:loc3+1] = tmplist.copy()  

            tmplist = new_y[loc1:loc2].copy()
            new_y[loc1:loc3-loc2+1+loc1] = new_y[loc2:loc3+1].copy()
            new_y[loc3-loc2+1+loc1:loc3+1] = tmplist.copy()

            
        new_path_count = 0
        for i in range(self.problem_size - 1):
            new_path_count += self.get_distance(i , i+1 , new_x , new_y)
            
        return new_path_count,new_x,new_y

    def accept(self,new_cost,new_x,new_y):
        self.path_count = new_cost
        self.coordinate_x = new_x.copy()
        self.coordinate_y = new_y.copy()


problem = Simulate_Anneal(150,"ch150.txt",1000)
problem.solve()


