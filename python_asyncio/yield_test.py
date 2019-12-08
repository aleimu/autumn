def ge1():
    yield 1


def ge2():
    a = yield from ge1()
    return a


for k in ge2():
    print(k)