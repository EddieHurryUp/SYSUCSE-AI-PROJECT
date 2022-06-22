import itertools
import queue
import time

class action:
    def __init__(self , action_name , parameters , preconditions , effect_adds , effect_dels):
        self.action_name = action_name
        self.parameters = parameters
        self.preconditions = preconditions
        self.effect_adds = effect_adds
        self.effect_dels = effect_dels

    def __str__(self):
        print("========================")
        print("action_name:" , self.action_name)
        print("parameters:" , self.parameters)
        print("preconditions:" , self.preconditions)
        print("effect_adds:" , self.effect_adds)
        print("effect_dels:", self.effect_dels)
        print("========================")
        return ""

class Node(object):
    def __init__(self, state, g, h , goal , acts):
        self.state = state
        self.g = g
        self.h = h
        self.f = self.g + self.h
        self.acts = acts
        self.goal = goal
    
    def __lt__(self, other):
        if self.f == other.f:
            return self.h < other.h
        else:
            return self.f < other.f

class pddl_planner:
    def __init__(self , actions , objects , init , goal , predicate_list):
        self.actions = actions
        self.objects = objects
        self.init = init
        self.goal = goal
        self.memory = {'state': [] , 'found_actions' : []}
        self.filled_actions = self.instantiate_actions()
        self.predicate_list = predicate_list
        
    def init_pro(self):
        for key in self.predicate_list:
            filled_para = self.fill(self.predicate_list[key])
            for para in filled_para:
                items = para.items()
                tmp = [key]
                for k , value in items:
                    tmp.append(value)
                new_pred = tuple(tmp)
                if new_pred not in self.init:
                    head = "not_" + new_pred[0]
                    tmp = [head]
                    for i in range(len(new_pred)):
                        if i > 0:
                            tmp.append(new_pred[i])
                    self.init.append(tuple(tmp))

    def fill(self , target):
        # print(target)
        result = []
        type_variable_map = dict()
        for type_group in self.objects:
            type_variable_map[type_group[-1]] = []
            for i in range(len(type_group) - 1):
                type_variable_map[type_group[-1]].append(type_group[i])

        type_variable_map1 = dict()        
        for para in target:
            vtype = para[1]
            if vtype in type_variable_map1:
                type_variable_map1[vtype].append(para[0])
            else:
                type_variable_map1[vtype] = []
                type_variable_map1[vtype].append(para[0])

        for key in type_variable_map1:
            filled = self.permutation(type_variable_map1[key] , type_variable_map[key])
            result.append(filled)

        merged_result = []    
        a = itertools.product(*result)
        for it in a:
            merge = it[0].copy()
            for dic in it:
                merge.update(dic)
            merged_result.append(merge)
        return merged_result
            
    def permutation(self , list1 , list2):
        result = []
        a = itertools.permutations(list2 , len(list1))
        for fill in a:
            dic = dict()
            for i in range(len(list1)):
                dic[list1[i]] = fill[i]
            result.append(dic)
        return result

    def instantiate_actions(self):
        filled_actions = []
        for i in range(len(self.actions['name'])):
            action_name = self.actions["name"][i]
            parameters = self.actions["parameters"][i]
            preconditions = self.actions["prec"][i]
            adds = self.actions['adds'][i]
            dels = self.actions['dels'][i]
            variable_map = self.fill(parameters)
            for map_version in variable_map:
                filled_preconditions = []
                filled_adds = []
                filled_dels = []
                for prec in preconditions:
                    filled_prec = [prec[0]]
                    i = 1
                    while i < len(prec):
                        filled_prec.append(map_version[prec[i]])
                        i += 1
                    filled_preconditions.append(tuple(filled_prec))

                for add in adds:
                    filled_add = [add[0]]
                    i = 1
                    while i < len(add):
                        filled_add.append(map_version[add[i]])
                        i += 1
                    filled_adds.append(tuple(filled_add))

                for _del in dels:
                    filled_del = [_del[0]]
                    i = 1
                    while i < len(_del):
                        filled_del.append(map_version[_del[i]])
                        i += 1
                    filled_dels.append(tuple(filled_del))

                new_action = action(action_name , map_version , filled_preconditions , filled_adds , filled_dels)
                filled_actions.append(new_action)
        return filled_actions
                    
    def goal_achieved(self , state):
        achieved = True
        for goal_item in self.goal:
            if goal_item not in state:
                achieved = False
                break
        return achieved

    def find_action(self, state):
        found_actions = []
        for act in self.filled_actions:
            valid_flag = True
            for prec in act.preconditions:
                if prec not in state:
                    valid_flag = False
                    break
            if valid_flag:
                found_actions.append(act)
        return found_actions
    
    def build_layers(self , state):
        layers = []
        new_layer = state.copy()
        while(1):
            layers.append(new_layer.copy())
            if set(self.goal) <= set(new_layer):
                break
            valid_actions = self.find_action(new_layer)
            # print(valid_actions[0])
            total_adds = []
            for act in valid_actions:
                for add in act.effect_adds:
                    total_adds.append(add)
            total_adds = list(set(total_adds))
            for add_it in total_adds:
                if add_it not in new_layer:
                    new_layer.append(add_it) 
        return layers

    def CountAction(self , goals , state_layer, cur_layer):
        if cur_layer == 0:
            return 0

        Gp = []
        Gn = []

        for goal in goals:
            if goal in state_layer[cur_layer-1]:
                Gp.append(goal)
            else:
                Gn.append(goal)

        usable_actions = self.find_action(state_layer[cur_layer-1])
        action_list = []
        adds_list = []
        for valid_action in usable_actions:
            adds = valid_action.effect_adds
            for add in adds:
                if add in Gn:
                    action_list.append(valid_action)
                    for add in adds:
                        adds_list.append(add)
                    break
            if set(Gn) <= set(adds_list):
                break
        
        goal_next = Gp.copy()
        for act in action_list:
            for prec in act.preconditions:
                if prec not in goal_next:
                    goal_next.append(prec)
        return len(action_list) + self.CountAction(goal_next, state_layer, cur_layer-1)
    
    def h_function(self,state):
        layers = self.build_layers(state)
        h = self.CountAction(self.goal, layers, len(layers)-1)
        return h

    def A_star_search(self):
        start_time = time.time()
        close = []
        q = queue.PriorityQueue()
        h = self.h_function(self.init)
        init_node = Node(self.init, 0, h , self.goal , [])
        q.put(init_node)
        
        pop_time = 0
        while not q.empty():
            head_node = q.get()
            close.append(head_node.state)
            pop_time += 1

            if self.goal_achieved(head_node.state):
                end_time = time.time()
                print("============================ result: ============================")
                for i in range(len(head_node.acts)):
                    action = head_node.acts[i]
                    print("step" , i , ": " , end='')
                    self.standard_output(action)
                print("============================ end: ============================")
                print("plan_time: " , end_time - start_time , "seconds.")
                print('pop_times: ' , pop_time)
                print("=================================================================")
                break
        
            valid_actions = self.find_action(head_node.state)
            for action in valid_actions:
                new_state = head_node.state.copy()
                acts = head_node.acts.copy()

                for add in action.effect_adds:
                    if add not in new_state:
                        new_state.append(add)

                for _del in action.effect_dels:
                    # print(action)
                    # print(_del)
                    new_state.remove(_del)

                if new_state not in close:
                    acts.append(action)
                    h = self.h_function(new_state)
                    new_node = Node(new_state, head_node.g+1 , h , self.goal , acts)
                    q.put(new_node)
                    close.append(new_state)

    def standard_output(self , action):
        action_name = action.action_name
        parameters = []
        for k , v in action.parameters.items():
            parameters.append(v)
        print(action_name , end='(')
        for i in range(len(parameters)):
            if i < len(parameters) - 1:
                print(parameters[i] , end = ' , ')
            else:
                print(parameters[i] , end = ')')
        print('\n')

    def plan(self):
        self.init_pro()
        self.A_star_search()

# actions , objects , init , goal , predicate_list  = parser("./PDDL/test4/test4_domain.txt" , "./PDDL/test4/test4_problem.txt").parse()
# plan = planner(actions , objects , init , goal , predicate_list)
# plan.init_pro()
# # print(plan.init)
# plan.plan()