__author__ = 'brian'

def thing(x):
    return x+5
# end def

if __name__ == "__main__":

    newFunc = thing

    lst = range(5)

    result = [ newFunc(x) for x in lst ]

    print 'lst    = ', lst
    print 'result = ', result