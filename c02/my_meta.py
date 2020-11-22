import yaml

class MyMeta(type):
    def __init__(cls, name, bases, dic):
        super().__init__(name, bases, dic)
        print('==>MyMeta.__init__')
        print('   cls.__name__: ', cls.__name__)
        print('   attributedict: ', dic)

    def __new__(cls, *args, **kwargs):
        print('==>MyMeta.__new__')
        print('   cls.__name__: ', cls.__name__)
        return type.__new__(cls, *args, **kwargs)

    def __call__(cls, *args, **kwargs):
        print('==>MyMeta.__call__')
        obj = cls.__new__(cls)
        cls.__init__(obj, *args, **kwargs)
        return obj

class MyClass(yaml.YAMLObject):
    yaml_tag = u'!MyClass'

    def __init__(self, name):
        print('==>MyClass.__init__')
        print('   self.__name__: ', self.__class__.__name__)
        self.name = 'super_' + name

    def __new__(cls, *args, **kwargs):
        # pylint: disable=unused-argument
        print('==>MyClass.__new__')
        print('   cls.__name__: ', cls.__name__)
        return object.__new__(cls)

    def __call__(self, *args, **kwargs):
        print('==>MyClass.__new__')
        print('   self: ', self)


class Foo(metaclass=MyMeta):
    # yaml_loader = yaml.SafeLoader
    yaml_tag = u'!Foo'

    def __init__(self, name, greeting):
        # __init__() 的参数 self，就是 __new__() 出来的实例返回
        # ? self.__class__.__name__ == MyMeta
        print(f'{self.__class__.__name__}.__init__')
        self.name = name
        self.greeting = greeting

    def __new__(cls, *args, **kwargs):
        # 静态方法，至少要传递一个参数 cls，cls 表示需要实例化的类
        # 必须要有返回值，返回实例化出来的实例，也可以返回 父类 或 object.__new__() 出来的实例
        print(f'{cls.__name__}.__new__')
        return object.__new__(cls, *args, **kwargs)

    def __repr__(self):
        print(f'{self.__class__.__name__}.__repr__')
        return f'{self.__class__.__name__}(name={self.name}, greeting={self.greeting})'

class Foo2(MyClass):
    yaml_tag = u'!Foo2'

    def __init__(self, name):
        super().__init__(name)
        # print(f'{self.__class__.__name__}.__init__')
        print(f'{type(self).__name__}.__init__')
        self.name = name

    def __new__(cls, *args, **kwargs):
        print(f'{cls.__name__}.__new__')
        return object.__new__(cls)


def run_test():
    foo = Foo('foo', 'hello world')
    print(yaml.dump(foo))
    print('----------')
    foo2 = Foo2('foo2')
    print(foo2.name)
    print(yaml.dump(foo2))
    print('----------')
    foo3 = MyClass('foo3')
    print(foo3.name)
    print(yaml.dump(foo3))
    print('----------')
    # # yaml.add_constructor(u'!Foo', Foo.__new__)
    # !!python/object:__main__.Foo
    data = yaml.load("""
--- !!python/object:__main__.Foo
name: Cave spider
greeting: Good Afternoon
""", Loader=yaml.FullLoader)
    print(data)
    print(yaml.dump(data))

if __name__ == "__main__":
    run_test()
