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
        # self.predicate_list = {}
        self.domain_filename = domain_filename
        self.problem_filename = problem_filename

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
        result.append('n' + "_" + find[1])
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
    
    def parse(self):
        self.domain_parser()
        self.problem_parser()
        # self.make_pred_list()
        self.actions = {
            "name": self.action_name,
            "parameters": self.parameters,
            "prec": self.preconditions,
            "adds": self.effect_adds,
            "dels": self.effect_dels
        }
        return  self.actions , self.objects , self.init , self.goal

# print(parser("./PDDL/test2/test2_domain.txt" , "./PDDL/test2/test2_problem.txt").parse()[0]['adds'])
# print(parser("./PDDL/test2/test2_domain.txt" , "./PDDL/test2/test2_problem.txt").parse()[1])
# actions , objects , init , goal  = pddl_parser("./PDDL/test5/test5_domain.txt" , "./PDDL/test5/test5_problem.txt").parse()
# # print(actions['prec'])
# # print(goal)
# print(actions['dels'])
