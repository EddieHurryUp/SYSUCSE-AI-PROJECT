from math import log2
from itertools import permutations
import re

def get_data():
    num = 0
    clauses = []
    num=int(input())
    for i in range(0, num):
        clause = []
        for item in re.findall(r'¬*[a-zA-Z]+\([a-zA-Z,\s]*\)', input()):
            items = re.findall(r'[¬a-zA-Z]+', item)
            clause.append(items)
        clauses.append(clause[0])
    return clauses
    
def cal_gain(m01 , m02 , m11 , m12):
    if(m11 == 0):
        return -999
    gain = m11 * ( log2( m11 / (m11 + m12)) - log2( m01 / (m01 + m02)))
    return gain

def get_background_rules_set(back_ground):
    background_rules = []
    tmp_set  = set()
    for it in back_ground:
        tmp_set.add(it[0])
    for it in list(tmp_set):
        background_rules.append((it , 'x' , 'y'))
        background_rules.append((it , 'y' , 'x'))
        background_rules.append((it , 'x' , 'z'))
        background_rules.append((it , 'z' , 'x'))
        background_rules.append((it , 'y' , 'z'))
        background_rules.append((it , 'z' , 'y'))
    return background_rules

def find_in_background(names , rules , back_ground):
    examples_in_background = []
    if len(rules) == 1:
        for rule in rules:
            for knowledge in back_ground:
                name_map = dict()
                name_map['x'] = 'default'
                name_map['y'] = 'default'
                name_map['z'] = 'default'
                if rule[0] == knowledge[0]:
                    name_map[rule[1]] = knowledge[1]
                    name_map[rule[2]] = knowledge[2]
                    examples_in_background.append((knowledge , name_map))
    if len(rules) == 2:
        name_combination = list(permutations(names , 3))
        for comb in name_combination:
            name_map = dict()
            name_map['x'] = comb[0]
            name_map['y'] = comb[1]
            name_map['z'] = comb[2]
            tmp0 = [rules[0][0] , name_map[rules[0][1]] , name_map[rules[0][2]]]
            tmp1 = [rules[1][0] , name_map[rules[1][1]] , name_map[rules[1][2]]]
            if (tmp0 in back_ground) and (tmp1 in back_ground) and (tmp0 != tmp1):
                examples_in_background.append((tmp0 , tmp1 , name_map))
    return examples_in_background

def find_tmp_covered(target , names, tmp , examples):
    tmp_covered = []
    expended_tmp = []
    if tmp['x'] != 'default' and tmp['y'] != 'default':
        expended_tmp.append([target , tmp['x'] , tmp['y']])
    if tmp['x'] == 'default':
        for name in names:
            expended_tmp.append([target , name , tmp['y']])
    if tmp['y'] == 'default':
        for name in names:
            expended_tmp.append([target , tmp['x'] , name])
    for it in expended_tmp:
        if it in examples:
            tmp_covered.append(it)
    return tmp_covered   

def find_covered(names , target , examples_in_background , negative_examples , positive_examples):
    pos_covered = []
    neg_covered = []
    for example in examples_in_background:
        if len(example) == 2:
            tmp = example[1]
        else:
            tmp = example[2]
        tmp_pos_covered = find_tmp_covered(target , names , tmp , positive_examples)
        tmp_neg_covered = find_tmp_covered(target , names , tmp , negative_examples)
        pos_covered += tmp_pos_covered
        neg_covered += tmp_neg_covered
    return pos_covered,neg_covered

def one_rule(names , target , rules , rule , back_ground , negative_examples , positive_examples):
    new_rules = rules.copy()
    new_rules.append(rule)
    examples_in_background = find_in_background(names , new_rules , back_ground)
    pos_covered , neg_covered = find_covered(names , target , examples_in_background , negative_examples , positive_examples) 
    new_pos_covered = []
    new_neg_covered = []
    for it in neg_covered:
        if it not in new_neg_covered:
            new_neg_covered.append(it)
    for it in pos_covered:
        if it not in new_pos_covered:
            new_pos_covered.append(it)
    return new_pos_covered , new_neg_covered


def get_target():
    return input().split("(")[0]

def get_pos_and_neg(clause , target):
    back_ground = []
    positive_examples = []
    negative_examples = [] 
    for it in clause:
        it = it.copy()
        if it[0] != target and it[0] != "¬" + target:
            back_ground.append(it)
            negative_examples.append([target, it[1] , it[2]])
        if it[0] == target:
            positive_examples.append(it)
    return back_ground , negative_examples , positive_examples

def get_names(clause):
    names = set()
    for it in clause:
        names.add(it[1])
        names.add(it[2])
    return list(names)

def solve(names , rules_set , target , back_ground , negative_examples , positive_examples):
    result = []
    m11 = len(positive_examples)
    m12 = len(negative_examples)
    m01 = m11
    m02 = m12
    i = 0
    old_gain = -9999
    while(1):
        i = i + 1
        new_rule = None
        saved_m11 = 0
        saved_m12 = 0
        saved_pos = positive_examples.copy()
        saved_neg = negative_examples.copy()
        for it in rules_set:
            pos , neg = one_rule(names , target , result , it , back_ground , negative_examples , positive_examples)
            m11 = len(pos)
            m12 = len(neg)
            gain = cal_gain(m01 , m02 , m11 , m12)
            if gain > old_gain:
                new_rule = it
                old_gain = gain
                saved_m11 = m11
                saved_m12 = m12
                saved_pos = pos
                saved_neg = neg
        positive_examples = saved_pos
        negative_examples = saved_neg
        result.append(new_rule)
        if saved_m12 == 0 and saved_m11 == len(positive_examples):
            break   
    return result,positive_examples
    
def ans_process(result , target):
    ans = ""
    condition = []
    for it in result:
        a = it[0]
        string = it[0] + "(" + it[1] + "," + it[2] + ")"
        condition.append(string)
    before = condition[0]
    if len(condition) == 2:
        before += " ∧  "
        before += condition[1]
    ans = before + " -> " + target + "(" + "x" + "," + "y" + ")"
    return ans


def main():
    clause = get_data()
    new_clause = []
    for it in clause:
        if len(it) == 3:
            new_clause.append(it)
    clause = new_clause
    target = get_target()
    back_ground , negative_examples , positive_examples = get_pos_and_neg(clause, target)
    rules_set = get_background_rules_set(back_ground)
    names = get_names(clause)
    result,fact = solve(names , rules_set , target , back_ground , negative_examples , positive_examples)
    print("===============================================")
    print(ans_process(result , target))
    fact = find_in_background(names , result , back_ground)
    for example in fact:
        if len(example) == 2:
            tmp = example[1]
        else:
            tmp = example[2]
        print(target + "(" + tmp['x'] + "," + tmp["y"] + ")")
    print("===============================================")
main()

