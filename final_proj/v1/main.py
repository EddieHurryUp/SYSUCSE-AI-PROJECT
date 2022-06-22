from parser import pddl_parser
from planner import pddl_planner

if __name__ == '__main__':
    print("*************************** problem list ***************************")
    print('0 - magic_word')
    print('1 - magic_world_plus')
    print('2 - magic_world_plus_plus')
    print('3 - blocksworld')
    print('4 - blocksworld_plus')
    print('5 - puzzle')
    print("********************************************************************")
    print("Please input the problem ID: (0-5)")
    id = input()
    domain_file = "./PDDL/test{}/test{}_domain.txt".format(id , id)
    problem_file = "./PDDL/test{}/test{}_problem.txt".format(id , id)
    actions , objects , init , goal  = pddl_parser(domain_file , problem_file).parse()
    planner = pddl_planner(actions , objects , init , goal)
    planner.plan()