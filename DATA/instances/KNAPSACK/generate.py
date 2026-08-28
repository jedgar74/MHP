# coding=UTF-8
"""Genera instancias reproducibles de 0/1 Knapsack y sus optimos exactos."""
import os
import random

ROOT = os.path.dirname(os.path.abspath(__file__))
OPT = os.path.join(ROOT, 'opt', 'optimums.txt')


def exact_optimum(values, weights, capacity):
    dp = [0] * (capacity + 1)
    for value, weight in zip(values, weights):
        for c in range(capacity, weight - 1, -1):
            dp[c] = max(dp[c], dp[c - weight] + value)
    return max(dp)


def write_instance(name, values, weights, capacity):
    path = os.path.join(ROOT, name + '.txt')
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write('# 0/1 Knapsack: n capacity; luego value weight\n')
        fh.write('%d %d\n' % (len(values), capacity))
        for value, weight in zip(values, weights):
            fh.write('%d %d\n' % (value, weight))
    return exact_optimum(values, weights, capacity)


def main():
    random.seed(20260828)
    os.makedirs(os.path.join(ROOT, 'opt'), exist_ok=True)

    optimums = {}

    # Instancia pequena de oraculo: optimo = objetos 2 y 3 -> valor 220, peso 50.
    values = [60, 100, 120]
    weights = [10, 20, 30]
    optimums['toy3'] = write_instance('toy3', values, weights, 50)

    # Banco de 10 instancias medianas. Mezcla items correlacionados y ruido para
    # evitar que ordenar solo por value/weight resuelva trivialmente el banco.
    for k in range(1, 11):
        n = 60
        weights = [random.randint(5, 100) for _ in range(n)]
        values = []
        for w in weights:
            base = int(1.7 * w)
            values.append(max(1, base + random.randint(-45, 80)))
        capacity = int(sum(weights) * (0.30 + 0.015 * (k % 5)))
        name = 'kp60_%02d' % k
        optimums[name] = write_instance(name, values, weights, capacity)

    with open(OPT, 'w', encoding='utf-8') as fh:
        for name in sorted(optimums):
            fh.write('%s %d\n' % (name, optimums[name]))

    print('Generadas %d instancias. Optimos en %s' % (len(optimums), OPT))


if __name__ == '__main__':
    main()
