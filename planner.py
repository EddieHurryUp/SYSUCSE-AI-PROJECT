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
        self.goal = goal
        self.acts = acts
    
    def __lt__(self, other):
        return self.f < other.f

class pddl_planner:
    def __init__(self , actions , objects , init , goal):
        self.actions = actions
        self.objects = objects
        self.init = init
        self.goal = goal
        self.memory = {'state': [] , 'found_actions' : []}
        self.filled_actions = self.instantiate_actions()
        # self.predicate_list = predicate_list
        
    # def init_pro(self):
    #     for key in self.predicate_list:
    #         filled_para = self.fill(self.predicate_list[key])
    #         for para in filled_para:
    #             items = para.items()
    #             tmp = [key]
    #             for k , value in items:
    #                 tmp.append(value)
    #             new_pred = tuple(tmp)
    #             if new_pred not in init:
    #                 head = "not_" + new_pred[0]
    #                 tmp = [head]
    #                 for i in range(len(new_pred)):
    #                     if i > 0:
    #                         tmp.append(new_pred[i])
    #                 self.init.append(tuple(tmp))

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
        valid_flag = True
        for g in self.goal:
            if g[0][0] == 'n' and g[0][1] == '_':
                new_prec = []
                new_head = ''
                for i in range(len(g[0])):
                    if i > 1:
                        new_head += g[0][i]
                new_prec.append(new_head)
                for i in range(len(g)):
                    if i > 0:
                        new_prec.append(g[i])
                new_prec = tuple(new_prec)
                if new_prec  in state:
                    valid_flag = False
                    break
                else:
                    valid_flag = True
            else:
                if g not in state:
                        # print(act.action_name)
                        # print(act.parameters)
                        # print(prec)
                    valid_flag = False
                    break
        return valid_flag

    # def check(self , act):
    #     if act.action_name == 'unstack' and act.parameters == {'a': 'b', 'b': 'a', 'x': 't1', 'y': 't2'}:
    #         return 1
    #     else:
    #         return 0

    def find_action(self, state):
        # if state in self.memory['state']:
        #      return self.memory['found_actions'][self.memory['state'].index(state)]
        # else:     
            found_actions = []
            for act in self.filled_actions:
                valid_flag = True
                for prec in act.preconditions:
                    if prec[0][0] == 'n' and prec[0][1] == '_':
                        new_prec = []
                        new_head = ''
                        for i in range(len(prec[0])):
                            if i > 1:
                                new_head += prec[0][i]
                        new_prec.append(new_head)
                        for i in range(len(prec)):
                            if i > 0:
                                new_prec.append(prec[i])
                        
                        new_prec = tuple(new_prec)
                        if new_prec  in state:
                            valid_flag = False
                            break
                        else:
                            valid_flag = True
                    else:
                        if prec not in state:
                            # print(act.action_name)
                            # print(act.parameters)
                            # print(prec)
                            valid_flag = False
                            break
                # if self.check(act):
                #         print(valid_flag)
                if valid_flag:
                    # if self.check(act):
                    #     print(act.effect_dels)
                    found_actions.append(act)
            # self.memory['state'].append(state)
            # self.memory['found_actions'].append(found_actions)
            return found_actions

    def relaxed_find_action(self, state):
        found_actions = []
        for act in self.filled_actions:
            valid_flag = True
            for prec in act.preconditions:
                if prec[0][0] == 'n' and prec[0][1] == '_':
                    valid_flag = True
                else: 
                    if prec not in state:
                        # if self.check(act):
                        #     print(prec)
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
            relaxed_goal = []
            for it in self.goal:
                if it[0][0] == 'n' and it[0][1] == '_':
                    continue
                relaxed_goal.append(it)

            if set(relaxed_goal) <= set(new_layer):
                break
            valid_actions = self.relaxed_find_action(new_layer)
            # print(valid_actions)
            # k = 0
            # while k < 1000000:
            #     k += 1
            total_adds = []
            for act in valid_actions:
                # print(act)
                for add in act.effect_adds:
                    total_adds.append(add)
            total_adds = list(set(total_adds))
            for add_it in total_adds:
                if add_it not in new_layer:
                    new_layer.append(add_it) 
            # print(new_layer)
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

            # relaxed_Gn = []
            # for it in Gn:
            #     if it[0][0] == 'n' and it[0][1] == '_':
            #         continue
            #     relaxed_Gn.append(it)
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
        # print("*")
        pop_time = 0
        while not q.empty():
            head_node = q.get()
            pop_time += 1
            # print(head_node.state)
            close.append(head_node.state)

            if self.goal_achieved(head_node.state):
                end_time = time.time()
                print("******* Plan Success! *******")
                print("Using time:" , end_time - start_time , 'seconds.' )
                print("Pop nodes:" , pop_time , "times")
                print("*****************************\n")

                print("============================ result: ============================")
                for i in range(len(head_node.acts)):
                    action = head_node.acts[i]
                    print("step" , i , ": " , end='')
                    self.standard_output(action)
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
        self.A_star_search()

# actions , objects , init , goal  = parser("./PDDL/test4/test4_domain.txt" , "./PDDL/test4/test4_problem.txt").parse()
# plan = planner(actions , objects , init , goal)
# plan.plan()