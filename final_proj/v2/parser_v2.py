import re
class pddl_parser:
    def __init__(self , domain_filename , problem_filename):
        self.action_name = []
        self.parameters = []
        self.preconditions = []
        self.effect_adds = []
        self.effect_dels = []
        self.objects = []
        self.init = []
        self.goal = []
        self.predicate_list = {}
        self.domain_filename = domain_filename
        self.problem_filename = problem_filename
    
    def neg(self , pre):
        head  = pre[0]
        new_pre = []
        if head[0] == 'n' and head[1] == 'o' and head[2] == 't':
            new_head = ''
            for i in range(len(head)):
                if i > 3:
                    new_head += head[i]
            new_pre.append(new_head)
            for i in range(len(pre)):
                if i > 0:
                    new_pre.append(pre[i])
        else:
            new_head = "not_" + head
            new_pre.append(new_head)
            for i in range(len(pre)):
                if i > 0:
                    new_pre.append(pre[i])
        return tuple(new_pre)

    def make_parameter(self , s):
        pattern = re.compile(r"\?(\w+) - (\w+)")
        return re.findall(pattern, s)[0]

    def make_object(self , s): # precondition effect
        if type(s) is not tuple:
            pattern = re.compile(r"(\w+)")
            return tuple(re.findall(pattern, s))
        else:
            return s
        
    def make_neg_precondition(self , s): # precondition effect
        pattern = re.compile(r"(\w+)")
        find = re.findall(pattern, s)
        result = []
        result.append(find[0] + "_" + find[1])
        index = 2
        while index < len(find):
            result.append(find[index])
            index += 1

        return tuple(result)

    def domain_parser(self):
        with open(self.domain_filename, "r") as f:
            lines = f.readlines()
            i = 0
            while i < len(lines):
                # 编译action
                if "action" not in lines[i]:
                    i += 1
                    continue
                
                line = lines[i].strip() 
                name_index = line.find("action") + 7 # action这个词有六个字母
                self.action_name.append(line[name_index:])

                # 编译parameters
                i += 1                                   
                line = lines[i].strip()
                pattern = re.compile(r"(?:\?\w+ - \w+)")
                parameters = re.findall(pattern, line)
                tmp = []
                for parameter in parameters:
                    tmp.append(self.make_parameter(parameter))
                self.parameters.append(tmp)
                
                # 编译precondition
                i += 1 
                line = lines[i].strip()
                line = line.replace("-" , "_")
                # print(line)
                pattern = re.compile(r"\((?!not \()(?:\w+)(?: \?\w+)+\)(?!\))")
                pattern1 = re.compile(r"\((?:not )\((?:\w+)(?: \?\w+)+\)(?:\))")
                preconditions = re.findall(pattern, line)
                neg_preconditions = re.findall(pattern1 , line)
                tmp = []
                for precondition in preconditions:
                    tmp.append(self.make_object(precondition))
                for precondition in neg_preconditions:
                    tmp.append(self.make_neg_precondition(precondition))

                self.preconditions.append(tmp)

                # 编译effect
                i += 1
                line = lines[i].strip()
                line = line.replace("-" , "_")
                pattern_add = re.compile(r"\((?!not \()(?:\w+)(?: \?\w+)+\)(?!\))")
                pattern_del = re.compile(r"\((?:not )\((?:\w+)(?: \?\w+)+\)(?:\))")
                adds = re.findall(pattern_add, line)                    
                dels = re.findall(pattern_del, line)

                tmp_add = []
                tmp_del = []
                for add in adds:
                    tmp_add.append(self.make_object(add))
                for delete in dels:
                    tmp_del.append(self.make_object(delete)[1:])

                neg_adds = []
                for add in tmp_add:
                    neg_adds.append(self.neg(add))
                neg_dels = []
                for _del in tmp_del:
                    neg_dels.append(self.neg(_del))

                for neg_add in neg_adds:
                    tmp_del.append(neg_add)
                for neg_del in neg_dels:
                    tmp_add.append(neg_del)
                
                self.effect_adds.append(tmp_add)
                self.effect_dels.append(tmp_del)
                i += 1

    # readin and parse problem file
    def problem_parser(self):
        with open(self.problem_filename, "r") as f:
            lines = f.readlines()
            i = 0
            while i < len(lines):
                if i == len(lines):
                    break
                line = lines[i].strip()

                if "objects" in line:
                    i += 1
                    line = lines[i].strip()
                    while line != ")":
                        if line:
                            self.objects.append(self.make_object(line))
                        i += 1
                        line = lines[i].strip()

                elif "init" in line:
                    i += 1
                    line = lines[i].strip()
                    while line != ")":
                        if line:
                            self.init.append(self.make_object(line))
                        i += 1
                        line = lines[i].strip()

                elif "goal" in line:
                    line = line.replace("-" , "_")
                    goal_str = re.compile(r"\((?!not \()(?:\w+)(?: \w+)+\)(?!\))")
                    neg_goal_str = re.compile(r"\((?:not \()(?:\w+)(?: \w+)+\)(?:\))")
                    goals = re.findall(goal_str, line)
                    neg_goals = re.findall(neg_goal_str , line)
                    for goal in goals:
                        self.goal.append(self.make_object(goal))
                    for neg_goal in neg_goals:
                        self.goal.append(self.make_neg_precondition(neg_goal)) 
                i += 1
    
    def find_type(self , obj , paras):
        for it in paras:
            if it[0] == obj:
                return it[1]

    def make_pred_list(self):
        # preds = []
        # for i in self.preconditions:
        #     preds += i
        for i in range(len(self.preconditions)):
            preds = self.preconditions[i]
            parameters = self.parameters[i]
            for it in preds:
                # print(it)
                if it[0][0] == 'n' and it[0][1] == 'o' and it[0][2] == 't':
                    pred = ''
                    for i in range(len(it[0])):
                        if i > 3:
                            pred += it[0][i]
                else:
                    pred = it[0]
                if (pred not in self.predicate_list):
                    tmp = []
                    for i in range(len(it)):
                        if  i > 0:
                            vtype = self.find_type(it[i] , parameters)
                            tmp.append((str(i) , vtype))
                    self.predicate_list[pred] = tmp

        for i in range(len(self.effect_adds)):
            preds = self.effect_adds[i]
            parameters = self.parameters[i]
            for it in preds:
                # print(it)
                if it[0][0] == 'n' and it[0][1] == 'o' and it[0][2] == 't':
                    pred = ''
                    for i in range(len(it[0])):
                        if i > 3:
                            pred += it[0][i]
                else:
                    pred = it[0]
                if pred not in self.predicate_list:
                    tmp = []
                    for i in range(len(it)):
                        if  i > 0:
                            vtype = self.find_type(it[i] , parameters)
                            tmp.append((str(i) , vtype))
                    self.predicate_list[pred] = tmp

        for i in range(len(self.effect_dels)):
            preds = self.effect_dels[i]
            parameters = self.parameters[i]
            for it in preds:
                # print(it)
                if it[0][0] == 'n' and it[0][1] == 'o' and it[0][2] == 't':
                    pred = ''
                    for i in range(len(it[0])):
                        if i > 3:
                            pred += it[0][i]
                else:
                    pred = it[0]

                if pred not in self.predicate_list:
                    tmp = []
                    for i in range(len(it)):
                        if  i > 0:
                            vtype = self.find_type(it[i] , parameters)
                            tmp.append((str(i) , vtype))
                    self.predicate_list[pred] = tmp                    
        #     pred = it[0]
        #     if pred not in self.predicate_list:
        #         tmp = []
        #         for i in range(len(it)):
        #             if  i > 0:
        #                 vtype = self.find_type(it[i])
        #                 tmp.append((str(i) , vtype))
        #         self.predicate_list[pred] = tmp
    
    def parse(self):
        self.domain_parser()
        self.problem_parser()
        self.make_pred_list()
        self.actions = {
            "name": self.action_name,
            "parameters": self.parameters,
            "prec": self.preconditions,
            "adds": self.effect_adds,
            "dels": self.effect_dels
        }
        return  self.actions , self.objects , self.init , self.goal , self.predicate_list

# print(parser("./PDDL/test2/test2_domain.txt" , "./PDDL/test2/test2_problem.txt").parse()[0]['adds'])
# print(parser("./PDDL/test2/test2_domain.txt" , "./PDDL/test2/test2_problem.txt").parse()[1])
# actions , objects , init , goal , predicate_list = parser("./PDDL/test4/test4_domain.txt" , "./PDDL/test4/test4_problem.txt").parse()
# print(actions['adds'])

