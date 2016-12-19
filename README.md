## Objects, Inheritance, and Polymorphism

*Sidd Singal (siddharth.singal@students.olin.edu)*
*James Jang (Byumho.Jang@students.olin.edu)*
*Programming Languages*
*Fall 2016*

The goal of this project is to implement a functional object system, or at least the surface of it, including inheritance and polymorphism. The following list specific goals of this project that we will go into detail:
1. Create class templates and objects from those classes. Classes should include states (instance variables) and behaviors (procedures).
2. Superclass other classes and inherit all states and behaviors from that super class.
3. Make uninstantiable abstract classes and leave implementation up to programmers.
4. Exhibit correct polymorphism on objects that have a superclass reference.

### Introduction

First things first, it is hard to write classes and objects on a single line, so we (re-)created the multiline functionality so a line can span multiple lines on our interpreter. Type in `#multi` to begin the multiline parsing. Type in `#end` to signal the end of the block.
```
imp> #multi
{
	print 5;
	print "hello";
	print true;
}
#end
```

Now, let's look at the structure of classes and objects in our system. Classes can be defined with any number of instance variables and functions, given that all names are unique. Each class will have a single implicit constructor that should take in as many arguments as there are instance variables. Functions can be defined as `ENotImplemented()` for abstract classes, but any concrete classes must not contain any `ENotImplemented()`.

Any subclasses must provide a superconstructor with as many arguments as there are instance variables in the superclass. The subclass's constructor can be responsible for collecting those values.

Other than above, we can expect inheritance and polymorphism to work as expected.


### Basics: Class Templates and Objects

*Create class templates and objects from those classes. Classes should include states (instance variables) and behaviors (functions).*

Creating a class requires a number of parameters:
* name
* superclass
* parameter
* functions (or procedures in our language)


```
#multi
class (
    name: pNAME
    superclass: pIDENTIFIER
    (instanceVariable:pNAME instanceVariable:pNAME instanceVariable:pNAME ...)
    (superconstructorArgument:pIDENTIFIER superconstructorArgument:pIDENTIFIER ...)
    (
        (name:pNAME (args:pNAMES) statements:pSTMT)
        (name:pNAME (args:pNAMES) statements:pSTMT)
        ...
    )
)
```

As an example, we are going to define a simple `Dog` class. We can ignore the superclass related fields for this objective by declaring `Object` as the superclass and using () to define the arguments to the superclass's constructor.

```
imp> #multi
class (
    Dog
    Object
    (name age type)
    ()
    (
        (bark (sound) print sound;)
        (growOlder (years) age <- (+ age (* 7 years));)
        (getName () print name;)
        (getAge () print age;)
    )
)
#end
Dog.Object defined
```

We can make an object by using the `new` keyword and providing all of the required arguments space delimited.

```
imp> new Dog("brosky" 10 "husky")
```

It isn't useful to just create an object if we can't use it. We need to assign it to a reference using the `ref` keyword.

```
imp> obj Dog huskaroo = new Dog("brosky" 10 "husky")
huskaroo of type Dog.Object got assigned a Dog.Object object
```

We can also call it's functions using the `with` keyword.

```
imp> (with huskaroo bark ("wolf"))
wolf
imp> (with huskaroo getAge ())
10
imp> (with huskaroo growOlder (5))
imp> (with huskaroo getAge ())
45
```

### Inheritance

*Superclass other classes and inherit all states and behaviors from that super class.*

Making a class that extends another class is easy. Let's define a non-subclass first.

```
imp> #multi
class (
    Animal
    Object
    (name age)
    ()
    (
        (growOlder (years) age <- (+ age years);)
        (getName () print name;)
        (getAge () print age;)
    )
)
#end
Animal.Object defined
```

Now we can define other classes that subclass `Animal`.

```
imp> #multi
class (
    Dog
    Animal
    (name age type)
    (name age)
    (
        (bark (sound) print sound;)
        (growOlder (years) age <- (+ age (* 7 years));)
    )
)
#end
Animal.Object defined
imp> obj Dog huskaroo = new Dog("brosky" 10 "husky")
huskaroo of type Dog.Object got assigned a Dog.Object object
imp> (with huskaroo bark ("wolf"))
wolf
imp> (with huskaroo getAge ())
10
imp> (with huskaroo growOlder (5))
imp> (with huskaroo getAge ())
45
```

The `Dog` object works exactly the same as before. However, we did not have to define `getName` and `getAge` again because they were already defined in `Animal`. We decided to override `growOlder` though because dogs gain 7 dog years supposedely for every real year. We were able to add dog specific functions like `bark` to this class. 

It will be easier for us to define more `Animal` classes as well!

```
imp> #multi
class (
    Cat
    Animal
    (name age)
    (name age)
    (
        (meow () print "meow";)
    )
)
#end
Cat.Animal.Object defined
```

Note that our version of this code does not allow you to overload methods.

### Abstract classes

*Make uninstantiable abstract classes and leave implementation up to programmers.*

Some classes are just not meant to be instantiated because all information might not be known from the beginning. For example, we know all animals make a sound, but the sound they make depends on the animal. What could happen if we made `Animal` abstract?

We can make classes abstract by adding the `abstract` keyword before them. 

```
imp> #multi
absclass (
    Animal
    Object
    (name age)
    ()
    (
        (makeNoise () <>)
        (getName () print name;)
        (getAge () print age;)
    )
)
#end
Animal.Object defined
```

In this case, we have marked `makeNoise` as abstract by marking `<>;` as the implementation. Of course, we should not be able to instantiate an `Animal` object.

```
imp> obj Animal a = new Animal("ricky" 3000)
Exception: Runtime error: Cannot instantiate an abstract class
```

Let's make a concrete subclass.

```
imp> #multi
class (
    Dog
    Animal
    (name age)
    (name age)
    (
        (makeNoise () print "bark";)
    )
)
#end
Dog.Animal.Object defined
imp> obj Dog huskaroo = new Dog("brosky" 10)
huskaroo of type Dog.Animal.Object got assigned a Dog.Animal.Object object
imp> (with huskaroo makeNoise ())
bark
imp> (with huskaroo getName ())
brosky
```

We are able successfully instantiate a `Dog` object and call functions defined in both the subclass `Dog` and the superclass `Animal`. Let's try one more thing...

```
imp> #multi
class (
    Cat
    Animal
    (name age)
    (name age)
    ()
)
#end
Exception: Runtime error: Cannot create a concrete class with an abstract method
```

Uh oh! Looks like we cannot make a concrete `Cat` class live above because we did not implement all unimplemented methods!

### Polymorphism

*Exhibit correct polymorphism on objects that have a superclass reference.*

The type of reference to an object should be able to be a superclass of the actual object. In other terms, any object assignments are okay as long as the object type IS the reference type.

Let's define some classes real quick to see what this might look like.

```
imp> #multi
absclass (
    Animal
    Object
    (name age)
    ()
    (
        (makeNoise () <>)
        (getName () print name;)
        (getAge () print age;)
    )
)
#end
Animal.Object defined
imp> #multi
class (
    Dog
    Animal
    (name age)
    (name age)
    (
        (makeNoise () print "bark";)
        (getAge () print (* 7 age);)
        (sickEm (person) print (concat "Just attacked " person);)
    )
)
#end
Dog.Animal.Object defined
imp> #multi
class (
    Cat
    Animal
    (name age)
    (name age)
    (
        (makeNoise () print "meow";)
    )
)
#end
Cat.Animal.Object defined
```

Let's summarize. We created an abstract `Animal` class that is waiting for a `makenoise` method to be implemented. `Dog` subclasses animal, implements `makeNoise`, overrides `getAge`, and defines `sickEm`. `Cat` just implements `makeNoise` because cats are pretty boring like that.

What happens when we try to create a `Cat` reference pointing to a `Dog` object?

```
imp> obj Cat d = new Dog("anotherdog" 10);
Exception: Runtime error Cannot instantiate because Dog.Animal.Object is not of type Cat.Animal.Object
```

This won't work because a `Dog` is not a `Cat`. We know a `Cat` is an `Animal`. Will the following work?

```
imp> obj Cat d = new Animal("kitty" 10);
Exception: Runtime error: Cannot instantiate an abstract class
```

Still won't work because an `Animal` is not a `Cat`. The opposite will still work though because, as we mentioned, a `Cat` is an `Animal`.

```
imp> obj Animal c = new Cat("kitty" 10);
c of type Animal.Object got assigned a Cat.Animal.Object object
imp> (with c makeNoise ())
meow
```

Polymorphism will have interesting effects with the `Dog`. To start off, let's make a `Dog` object.

```
imp> obj Animal d = new Dog("doggy" 10)
d of type Animal.Object got assigned a Dog.Animal.Object object
imp> (with d makeNoise ())
bark
```

`makeNoise` works as intended. What about `sickEm`?

```
imp> (with d sickEm ("james"))
Exception: Runtime error: this function is not accessible or does not exist.
```

We would expect this to work, but it doesn't because `Animal` doesn't recognize any objects having a `sickEm`, so we can't use that method. Last but not least, what about `getAge`? Will it use `Animal`s implementation or `Dog`s?

```
imp> (with d getAge ());
70
```

It used `Dog`s! As expected from polymorphism.
