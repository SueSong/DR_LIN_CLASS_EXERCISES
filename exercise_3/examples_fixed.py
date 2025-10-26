# 1) Fixed subtle scope: do not assign to outer name inside; just read it
def outer():
    x = 1
    def inner():
        print(x)
        y = 2  # different local name
    inner()


# 2) Fixed global/local mixing
count = 0
def increment():
    global count
    count += 1


# 3) Fixed nested scope without nonlocal (return value instead)
def outer2():
    def middle():
        x = 0
        def inner(val):
            return val + 1
        x = inner(x)
    middle()


# 4) Fixed class vs instance/class attribute access
class MyClass:
    class_var = 1
    def method(self):
        print(self.class_var)


