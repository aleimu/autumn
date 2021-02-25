* Go优秀的文章合集

  * 新手50坑 https://segmentfault.com/a/1190000013739000#articleHeader43
  * Go问答101 https://gfw.go101.org/article/unofficial-faq.html#unaddressable-values 
  * Go语言高级编程 https://chai2010.cn/advanced-go-programming-book/
  * Go语言圣经中文版 https://chai2010.cn/advanced-go-programming-book/
  
* 可转换的类型之间,肯定是底层数据结构是一样的.

* 对于每一个类型T，都有一个对应的类型转换操作T(x)，用于将x转为T类型（译注：如果T是指针类型，可能会需要用小括弧包装T，比如(*int)(0)）。只有当两个类型的底层基础类型相同时，才允许这种转型操作，或者是两者都是指向相同底层结构的指针类型，这些转换只改变类型而不会影响值本身。如果x是可以赋值给T类型的值，那么x必然也可以被转为T类型，但是一般没有这个必要。  

* 在Go中，函数被看作第一类值（first-class values）：函数像其他值一样，拥有类型，可以被赋值给其他变量，传递给函数，从函数返回。对函数值（function value）的调用类似函数调用

    ```go
    func square(n int) int { return n * n }
    func negative(n int) int { return -n }
    func product(m, n int) int { return m * n }
    
    f := square
    fmt.Println(f(3)) // "9"
    
    f = negative
    fmt.Println(f(3))     // "-3"
    fmt.Printf("%T\n", f) // "func(int) int"
    
    f = product // compile error: can't assign func(int, int) int to func(int) int
    // 函数类型的零值是nil。调用值为nil的函数值会引起panic错误
    var f func(int) int
    f(3) // 此处f的值为nil, 会引起panic错误
    // 函数值可以与nil比较：
    var f func(int) int
    if f != nil {
    	f(3)
    }
    ```

* var 定义变量,没有显式初始化则被隐式赋予类型的零值(数值类型的零值是0,字符串的零值是"")

* var s string; s+="s",s前后的内存地址没变,`go-v.1.11`,难道之前是会变的吗?字符串是不可变的? -- string 类型的值是常量，不可更改!

* 将一个整数转为字符串，一种方法是用`fmt.Sprintf("%d", 123)`返回一个格式化的字符串；另一个方法是用`strconv.Itoa(“整数到ASCII”)`：

* 一个原生的字符串面值形式是`...`，使用反引号代替双引号。在原生的字符串面值中，没有转义操作；全部的内容都是字面的意思，包含退格和换行，因此一个程序中的原生字符串面值可能跨越多行

* string 与 byte slice 之间的转换,参与转换的是拷贝的原始值。这种转换的过程，与其他编程语的强制类型转换操作不同，也和新 slice 与旧 slice 共享底层数组不同。Go 在 string 与 byte slice 相互转换上优化了两点，避免了额外的内存分配：

  * 在 `map[string]` 中查找 key 时，使用了对应的 `[]byte`，避免做 `m[string(key)]` 的内存分配
  * 使用 `for range` 迭代 string 转换为 []byte 的迭代：`for i,v := range []byte(str) {...}`
  * `for range` 迭代会尝试将 string 翻译为 `UTF8` 文本，对任何无效的码点都直接使用 `0XFFFD rune（�）UNicode `替代字符来表示。如果 string 中有任何非 `UTF8` 的数据，应将 string 保存为 byte slice 再进行操作。

* 字符串的长度,Go 的内建函数 `len()` 返回的是字符串的 byte 数量，而不是像 Python 中那样是计算 Unicode 字符数。如果要得到字符串的字符数，可使用 `"unicode/utf8"` 包中的 `RuneCountInString(str string) (n int)`

* slice 中隐藏的数据

  ```go
  //从 slice 中重新切出新 slice 时，新 slice 会引用原 slice 的底层数组。如果跳了这个坑，程序可能会分配大量的临时 slice 来指向原底层数组的部分数据，将导致难以预料的内存使用。
  func get() []byte {
      raw := make([]byte, 10000)
      fmt.Println(len(raw), cap(raw), &raw[0])    // 10000 10000 0xc420080000
      return raw[:3]    // 重新分配容量为 10000 的 slice
  }
  
  func main() {
      data := get()
      fmt.Println(len(data), cap(data), &data[0])    // 3 10000 0xc420080000
  }
  // 可以通过拷贝临时 slice 的数据，而不是重新切片来解决：
  func get() (res []byte) {
      raw := make([]byte, 10000)
      fmt.Println(len(raw), cap(raw), &raw[0])    // 10000 10000 0xc420080000
      res = make([]byte, 3)
      copy(res, raw[:3])
      return
  }
  ```

* range迭代map,顺序是不固定的

* for 语句中的迭代变量与闭包函数

  ```go
  // for 语句中的迭代变量在每次迭代中都会重用，即 for 中创建的闭包函数接收到的参数始终是同一个变量，在 goroutine 开始执行时都会得到同一个迭代值
  type field struct {
      name string
  }
  
  func (p *field) print() {
      fmt.Println(p.name)
  }
  
  // 错误示例
  func main() {
      data := []field{{"one"}, {"two"}, {"three"}}
      for _, v := range data {
          go v.print()
      }
      time.Sleep(3 * time.Second)
      // 输出 three three three 
  }
  
  
  // 正确示例
  func main() {
      data := []field{{"one"}, {"two"}, {"three"}}
      for _, v := range data {
          v := v	//无需修改 goroutine 函数，在 for 内部使用局部变量保存迭代值，再传参
          go v.print()
      }
      time.Sleep(3 * time.Second)
      // 输出 one two three
  }
  
  // 正确示例
  func main() {
      data := []*field{{"one"}, {"two"}, {"three"}}
      for _, v := range data {    // 此时迭代值 v 是三个元素值的地址，每次 v 指向的值不同
          go v.print() //直接将当前的迭代值以参数形式传递给匿名函数
      }
      time.Sleep(3 * time.Second)
      // 输出 one two three
  }
  ```

* 在 range 迭代 slice、array、map 时通过更新引用来更新元素,在 range 迭代中，得到的值其实是元素的一份值拷贝，更新拷贝并不会更改原来的元素，即是拷贝的地址并不是原有元素的地址：

  ```go
  func main() {
      data := []int{1, 2, 3}
      for _, v := range data {
          v *= 10        // data 中原有元素是不会被修改的
      }
      fmt.Println("data: ", data)    // data:  [1 2 3]
  }
  //如果要修改原有元素的值，应该使用索引直接访问
  func main() {
      data := []int{1, 2, 3}
      for i, v := range data {
          data[i] = v * 10    
      }
      fmt.Println("data: ", data)    // data:  [10 20 30]
  }
  //如果你的集合保存的是指向值的指针，需稍作修改。依旧需要使用索引访问元素，不过可以使用 range 出来的元素直接更新原有值：
  func main() {
      data := []*struct{ num int }{{1}, {2}, {3},}
      for _, v := range data {
          v.num *= 10    // 直接使用指针更新
      }
      fmt.Println(data[0], data[1], data[2])    // &{10} &{20} &{30}
  }
  ```

* 运算符优先级:

  ```go
  Precedence    Operator
      5             *  /  %  <<  >>  &  &^
      4             +  -  |  ^
      3             ==  !=  <  <=  >  >=
      2             &&
      1             ||
  ```

* 所有的值类型变量在赋值和作为参数传递时都将产生一次复制动作.如果将数组作为函数的参数类型，则在函数调用时该参数将发生数据复制. (在函数体中，函数的形参作为局部变量，被初始化为调用者提供的值。函数的形参和有名返回值作为函数最外层的局部变量，被存储在相同的词法块中。实参通过值的方式传递，因此函数的形参是实参的拷贝。对形参进行修改不会影响实参。但是，如果实参包括引用类型，如指针，slice(切片)、map、function、channel等类型，实参可能会由于函数的间接引用被修改。因此，在函数体中无法修改传入的数组的内容，因为函数内操作的只是所传入数组的一个副本.)

* ```go var v3 [10]int    // 数组 ---数组有固定长度
  // 数组的长度必须是常量表达式，因为数组的长度需要在编译阶段确定
  var v31 [...]int{1,2,3,4}// 数组 --- "..."会推断数组的长度
  var v4 []int      // 切片 ，只定义
  v41 := []int{} // 切片，定义并赋值 
  a := [3]int{1, 2}              // 未初始化元素值为 0.
  b := [...]int{1, 2, 3, 4}      // 通过初始化值确定数组长度.------> ... 可以推断数组长度
  c := [5]int{2: 100, 4:200}     // 使用索引号初始化元素.
  ```

* 内存泄露的场景 https://gfw.go101.org/article/memory-leaking.html , 如:子字符串造成的暂时性内存泄露

* 在Go中，下列种类的类型的值可以有间接底层部分：

  - 字符串类型
  - 函数类型
  - 切片类型
  - 映射类型
  - 数据通道类型
  - 接口类型

* 哪些种类型的值可以用做内置`len`（以及`cap`、`close`、`delete`和`make`）函数调用的实参？可以被用做内置函数`len`调用的参数的值的类型都可以被称为（广义上的）容器类型。 这些容器类型的值都可以跟在`for-range`循环的`range`关键字后。

  |                    | len  | cap  | close | delete | make |
  | :----------------: | :--: | :--: | :---: | :----: | :--: |
  |      字符串值      | 可以 |      |       |        |      |
  | 数组或者数组指针值 | 可以 | 可以 |       |        |      |
  |       切片值       | 可以 | 可以 |       |        | 可以 |
  |       映射值       | 可以 |      |       |  可以  | 可以 |
  |     数据通道值     | 可以 | 可以 | 可以  |        | 可以 |

  

* 各种容器类型比较

  |   类型   | 容器值是否支持添加新的元素？ | 容器值中的元素是否可以被替换？ | 容器值中的元素是否可寻址？ | 访问容器值元素是否会更改容器长度？ | 容器值是否可以有间接底层部分？ |
  | :------: | :--------------------------: | :----------------------------: | :------------------------: | :--------------------------------: | :----------------------------: |
  |  字符串  |              否              |               否               |             否             |                 否                 |             是(1)              |
  |   数组   |              否              |             是(2)              |           是(2)            |                 否                 |               否               |
  |   切片   |            否(3)             |               是               |             是             |                 否                 |               是               |
  |   映射   |              是              |               是               |             否             |                 否                 |               是               |
  | 数据通道 |            是(4)             |               否               |             否             |                 是                 |               是               |

  (1) 对于标准编译器和运行时来说。 
  (2) 对于可寻址的数组值来说。 
  (3) 一般说来，一个切片的长度只能通过将另外一个切片赋值给它来被整体替换修改，这里我们不视这种情况为“添加新的元素”。 其实，切片的长度也可以通过调用`reflect.SetLen`来单独修改。增加切片的长度可以看作是一种变相的向切片添加元素。 但`reflect.SetLen`函数的效率很低，因此很少使用。 
  (4) 对于带缓冲并且缓冲未满的数据通道来说。

  

* 各类型的尺寸（对标准编译器1.12来说）。 在此表中，一个word表示一个原生字。在32位系统架构中，一个word为4个字节；而在64位系统架构中，一个word为8个字节。

  |             类型种类              |                            值尺寸                            | [Go白皮书](https://golang.google.cn/ref/spec#Numeric_types)中的[要求](https://golang.google.cn/ref/spec#Size_and_alignment_guarantees) |
  | :-------------------------------: | :----------------------------------------------------------: | :----------------------------------------------------------: |
  |               布尔                |                            1 byte                            |                         未做特别要求                         |
  |        int8, uint8 (byte)         |                            1 byte                            |                            1 byte                            |
  |           int16, uint16           |                           2 bytes                            |                           2 bytes                            |
  |   int32 (rune), uint32, float32   |                           4 bytes                            |                           4 bytes                            |
  | int64, uint64, float64, complex64 |                           8 bytes                            |                           8 bytes                            |
  |            complex128             |                           16 bytes                           |                           16 bytes                           |
  |             int, uint             |                            1 word                            | 架构相关，在32位系统架构中为4个字节，而在64位系统架构中为8个字节 |
  |              uintptr              |                            1 word                            |                  必须足够存下任一个内存地址                  |
  |              字符串               |                           2 words                            |                         未做特别要求                         |
  |               指针                |                            1 word                            |                         未做特别要求                         |
  |               切片                |                           3 words                            |                         未做特别要求                         |
  |               映射                |                            1 word                            |                         未做特别要求                         |
  |             数据通道              |                            1 word                            |                         未做特别要求                         |
  |               函数                |                            1 word                            |                         未做特别要求                         |
  |               接口                |                           2 words                            |                         未做特别要求                         |
  |              结构体               | 所有字段尺寸之和加上所有[填充的字节](https://gfw.go101.org/article/memory-layout.html#size-and-padding) |      一个不含任何尺寸大于零的字段的结构体类型的尺寸为零      |
  |               数组                |                    元素类型的尺寸 * 长度                     |          一个元素类型的尺寸为零的数组类型的尺寸为零          |

* 哪些表达式的估值结果可以包含一个额外的可选的值？

  |     语法     | 额外的可选的值（语法示例中的`ok`）的含义 |  舍弃额外的可选的值会对估值行为发生影响吗？   |                                                              |
  | :----------: | :--------------------------------------: | :-------------------------------------------: | ------------------------------------------------------------ |
  | 映射元素访问 |           `e, ok = aMap[key]`            |     键值`key`对应的条目是否存储在映射值中     | 否                                                           |
  |   数据接收   |          `e, ok = <- aChannel`           | 被接收到的值`e`是否是在数据通道关闭之前发送的 | 否                                                           |
  |   类型断言   |        `v, ok = anInterface.(T)`         |         接口值的动态类型是否为类型`T`         | 是 （当可选的值被舍弃并且断言失败的的时候，将产生一个恐慌。） |

* 几种导致当前协程永久阻塞的方法

  无需引入任何包，我们可以使用下面几种方法使当前协程永久阻塞：

  1. 向一个永不会被接收数据的数据通道发送数据。

     ```go
     make(chan struct{}) <- struct{}{}
     // 或者
     make(chan<- struct{}) <- struct{}{}
     ```

  2. 从一个未被并且将来也不会被发送数据的（并且保证永不会被关闭的）数据通道读取数据。

     ```go
     <-make(chan struct{})
     // 或者
     <-make(<-chan struct{})
     // 或者
     for range make(<-chan struct{}) {}
     ```

  3. 从一个nil数据通道读取或者发送数据。

     ```go
     chan struct{}(nil) <- struct{}{}
     // 或者
     <-chan struct{}(nil)
     // 或者
     for range chan struct{}(nil) {}
     ```

  4. 使用一个不含任何分支的select流程控制代码块。

     ```go
     select{}
     ```

* 哪些值可以被取地址，哪些值不可以被取地址？

  以下的值是不可以寻址的：

  - 字符串的字节元素
  - 映射元素
  - 接口值的动态值（类型断言的结果）
  - 常量值
  - 字面值
  - 声明的包级别函数
  - 方法（用做函数值）
  - 中间结果值
    - 函数调用
    - 显式值转换
    - 各种操作，不包含指针解引用（dereference）操作，但是包含：
      - 数据通道接收操作
      - 子字符串操作
      - 子切片操作
      - 加法、减法、乘法、以及除法等等。

  请注意：`&T{}`在Go里是一个语法糖，它是`tmp := T{}; (&tmp)`的简写形式。 所以`&T{}`是合法的并不代表字面值`T{}`是可寻址的。

  以下的值是可寻址的，因此可以被取地址：

  - 变量
  - 可寻址的结构体的字段
  - 可寻址的数组的元素
  - 任意切片的元素（无论是可寻址切片或不可寻址切片）
  - 指针解引用（dereference）操作

* 元素类型是自身

    ```go
    /*
    一个切片类型的元素类型可以是此切片类型自身，
    一个映射类型的元素类型可以是此映射类型自身，
    一个数据通道类型的元素类型可以是此数据通道类型自身，
    一个函数类型的输入参数和返回结果值类型可以是此函数类型自身。
    */
    package main

    func main() {
        type S []S
        type M map[string]M
        type C chan C
        type F func(F) F

        s := S{0:nil}
        s[0] = s
        m := M{"Go": nil}
        m["Go"] = m
        c := make(C, 3)
        c <- c; c <- c; c <- c
        var f F
        f = func(F)F {return f}

        _ = s[0][0][0][0][0][0][0][0]
        _ = m["Go"]["Go"]["Go"]["Go"]
        <-<-<-c
        f(f(f(f(f))))
    }
    ```

* 编译时刻断言技巧

    ```go
    // 下面任一行均可保证N >= M
    func _(x []int) {_ = x[N-M]}
    func _(){_ = []int{N-M: 0}}
    func _([N-M]int){}
    var _ [N-M]int
    const _ uint = N-M
    type _ [N-M]int

    // 如果M和N都是正整数常量，则我们也可以使用下一行所示的方法。
    var _ uint = N/M - 1
    var _ = map[bool]struct{}{false: struct{}{}, N>=M: struct{}{}}
    var _ = map[bool]int{false: 0, N>=M: 1}
    //断言两个整数常量相等的方法
    var _ [N-M]int; var _ [M-N]int
    type _ [N-M]int; type _ [M-N]int
    const _, _ uint = N-M, M-N
    func _([N-M]int, [M-N]int) {}
    var _ = map[bool]int{false: 0, M==N: 1}
    var _ = [1]int{M-N: 0} // 唯一被允许的元素索引下标为0
    var _ = [1]int{}[M-N]  // 唯一被允许的元素索引下标为0
    var _ [N-M]int = [M-N]int{}
    //断言一个常量字符串是不是一个空串的方法
    type _ [len(aStringConstant)-1]int
    var _ = map[bool]int{false: 0, aStringConstant != "": 1}
    var _ = aStringConstant[:1]
    var _ = aStringConstant[0]
    const _ = 1/len(aStringConstant)

    ```



* 变量覆盖

    ```go
    func main() {
      x := 1
      println(x)        // 1
      {
          println(x)    // 1
          x := 2
          println(x)    // 2    // 新的 x 变量的作用域只在代码块内部
      }
      println(x)        // 1
    }
    ```

* 显式类型的变量无法使用 nil 来初始化

    ```go
    // nil 是 interface、function、pointer、map、slice 和 channel 类型变量的默认初始值。但声明时不指定类型，编译器也无法推断出变量的具体类型。
    // 错误示例
    func main() {
      var x = nil    // error: use of untyped nil
      _ = x
    }
    // 正确示例
    func main() {
      var x interface{} = nil
      _ = x
    }    
    ```

* 调用函数返回的是值，并不是一个可取地址的变量

*   如果考虑效率的话，较大的结构体通常会用指针的方式传入和返回, 如果要在函数内部修改结构体成员的话，用指针传入是必须的；因为在Go语言中，所有的函数参数都是值拷贝传入的，函数参数将不再是函数调用时的原始变量。

* Circle和Wheel各自都有一个匿名成员。我们可以说Point类型被嵌入到了Circle结构体，同时Circle类型被嵌入到了Wheel结构体。

    ```go
    type Circle struct {
      Point
      Radius int
    }

    type Wheel struct {
      Circle
      Spokes int
    }
    /*
    得意于匿名嵌入的特性，我们可以直接访问叶子属性而不需要给出完整的路径
    一个命名为S的结构体类型将不能再包含S类型的成员：因为一个聚合的值不能包含它自身。（该限制同样适应于数组。）但是S类型的结构体可以包含*S指针类型的成员，这可以让我们创建递归的数据结构，比如链表和树结构等。
    外层的结构体不仅仅是获得了匿名成员类型的所有成员，而且也获得了该类型导出的全部的方法。这个机制可以用于将一个有简单行为的对象组合成有复杂行为的对象。组合是Go语言中面向对象编程的核心
    */
    ```

- 一种将slice元素循环向左旋转n个元素的方法是三次调用reverse反转函数，第一次是反转开头的n个元素，然后是反转剩下的元素，最后是反转整个slice的元素。（如果是向右循环旋转，则将第三个函数调用移到第一个调用位置就可以了。）

  ```go
    s := []int{0, 1, 2, 3, 4, 5}
    // Rotate s left by two positions.
    reverse(s[:2])
    reverse(s[2:])
    reverse(s)
    fmt.Println(s) // "[2 3 4 5 0 1]"
  ```



  



