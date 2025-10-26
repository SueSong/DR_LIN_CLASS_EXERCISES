# 1) Subtle scope confusion (should flag EUL001)
def outer():
    x = 1
    def inner():
        print(x)
        x = 2
    inner()


# 2) Global vs local mixing (should flag EUL002/EUL001)
count = 0
def increment():
    count += 1


# 3) Invalid nonlocal (should flag ENL001)
def outer2():
    def middle():
        def inner():
            nonlocal x
            x = 1
        inner()
    middle()


# 4) Class var bare access in method (should flag ECV001)
class MyClass:
    class_var = 1
    def method(self):
        print(class_var)


