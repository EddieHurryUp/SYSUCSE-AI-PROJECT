# coding:utf:8
import random

# 滑动变异
def slide_mutation(s):
    a, b = get_two_randint(len(s))
    t = s[a]
    for i in range(a + 1, b + 1):
        s[i - 1] = s[i]
    s[b] = t
    return s


# 倒置变异
def inversion_mutation(s):
    # 自己手写的2变换
    a, b = get_two_randint(len(s))
    for i in range(a, (a + b) // 2 + 1):
        s[i], s[b + a - i] = s[b + a - i], s[i]

    return s


# 返回（小，大）两个随机数
def get_two_randint(size):
    b = a = random.randint(0, size - 1)
    while a == b:
        b = random.randint(0, size - 1)

    if a > b:
        return b, a
    return a, b


# irgibnnm
def irgibnnm_mutation(s, distmat):
    a, b = get_two_randint(len(s))
    # 先inversion
    for i in range(a, (a + b) // 2 + 1):
        s[i], s[b + a - i] = s[b + a - i], s[i]

    # 再RGIBNNM
    b = (b + 1) % len(s)

    min = b - 1
    for i in range(len(s)):
        if i == b:
            continue
        if distmat[b][min] > distmat[b][i]:
            min = i
    s[b], s[min - 4] = s[min - 4], s[b]

    return s