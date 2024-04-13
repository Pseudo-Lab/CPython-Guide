# 레퍼런스 카운팅과 가비지 컬렉션

## 참조 카운팅(레퍼런스 카운팅)

### 용어 설명
- PyMem API : PyMem API는 CPython에서 메모리 할당 및 해제를 위해 사용되는 C 함수들의 모음입니다. 이 API는 Python 객체의 생성, 크기 조정 및 해제를 담당합니다.
- PyObject: Python 객체를 나타내는 C 구조체입니다. 모든 Python 객체는 PyObject 구조체로 표현됩니다. PyObject는 객체의 타입과 참조 카운트 등의 정보를 포함하고 있습니다.

CPython은 C의 동적 메모리 할당 시스템을 기반으로 구축되어 있습니다. 메모리 요구 사항은 런타임에 결정되며, PyMem API를 사용하여 시스템에 메모리가 할당됩니다. CPython은 메모리 관리를 위해 참조 카운팅[^1]과 가비지 컬렉션[^2]이라는 두 가지 전략을 사용합니다. 

### 참조 카운팅
#### 파이썬에서 변수 생성 과정
참조 카운팅은 객체에 대한 참조 수를 추적하는 메모리 관리 기법입니다. 객체를 참조하는 변수나 다른 객체가 있는 한 해당 객체는 메모리에서 해제되지 않습니다. 참조 수가 0이 되면 더 이상 필요하지 않은 것으로 간주되어 자동으로 메모리에서 해제됩니다.

```python
my_variable = ['a', 'b', 'c']
```

위 코드에서 `my_variable` 변수에 리스트 객체가 할당됩니다. 이 때 리스트 객체의 참조 수는 1이 됩니다. `my_variable`이 유효한 동안에는 리스트 객체의 메모리가 해제되어서는 안됩니다.

Python은 변수가 생성될 때, 해당 변수 이름이 현재 스코프의 로컬 변수(`locals()`) 또는 전역 변수(`globals()`) 딕셔너리에 존재하는지 확인합니다. 만약 존재하지 않는다면, 새로운 객체가 생성되고 해당 객체의 참조(포인터)가 로컬 변수 딕셔너리에 저장됩니다.

이를 확인하는 방법은 다음과 같습니다.
```python
def test_function():
    my_variable = ['a', 'b', 'c']
    print("my_variable in locals():", 'my_variable' in locals())
    print("my_variable in globals():", 'my_variable' in globals())
```

위 코드를 실행하면 다음과 같은 결과가 출력됩니다.
```python
>>> test_function()
my_variable in locals(): True
my_variable in globals(): False
```
이는 `my_variable`이 `test_function()`의 로컬 변수 딕셔너리에 존재하지만, 전역 변수 딕셔너리에는 존재하지 않음을 보여줍니다.

#### 참조 카운트 증가시키기
CPython의 소스 코드에는 `Py_INCREF()`와 `Py_DECREF()` 매크로가 Python 객체에 대한 참조를 증가시키고 감소시키는 API입니다.
- 참조 증가(`Py_INCREF`): 객체가 변수에 할당되거나, 함수/메서드의 인수로 전달되거나, 함수에서 반환될 때 호출됩니다.
- 참조 감소(`Py_DECREF`): 변수가 선언된 범위를 벗어나면 호출됩니다. 참조 수가 0이 되면 객체의 메모리가 해제됩니다.

CPython 소스코드에서 `Py_INCREF`는 단순히 `ob_refcnt` 값을 1 증가시킵니다. `ob_refcnt`는 `PyObject` 인스턴스의 프로퍼티로, 객체의 참조 카운터입니다.

```c
static inline void _Py_INCREF(PyObject *op)
{
#ifdef Py_REF_DEBUG
    _Py_RefTotal++;
#endif
    op->ob_refcnt++;
}
```

- `PyObject`는 파이썬 객체를 나타내는 C 구조체입니다.
- `op`는 `PyObject` 포인터 변수로, 파이썬 객체의 메모리 주소를 저장합니다.
- `#ifdef Py_REF_DEBUG` ~ `#endif`
    - 이는 C 전처리기 지시자로, 조건부 컴파일을 위해 사용됩니다.
    - `#ifdef`는 "if defined"의 줄임말로, `Py_REF_DEBUG`라는 매크로가 정의되어 있는지 확인합니다.
    - 만약 `Py_REF_DEBUG`가 정의되어 있다면, `#ifdef`와 `#endif` 사이의 코드가 컴파일됩니다. 그렇지 않으면 해당 코드는 무시됩니다.
    - `Py_REF_DEBUG`는 디버깅 용도로 사용되는 매크로로, 참조 카운팅 관련 디버깅 정보를 추적하는 데 사용됩니다.
-  `_Py_RefTotal++;`, `op->ob_refcnt++;`
    - `_Py_RefTotal`은 참조 카운팅 디버깅을 위해 사용됩니다. 이 변수는 `Py_REF_DEBUG`가 정의되어 있을 때만 증가합니다.
    - `op->ob_refcnt`는 `PyObject` 구조체의 `ob_refcnt` 필드에 접근하는 코드입니다. 이 필드는 해당 객체의 참조 카운트를 저장합니다.

Python 코드로 참조 카운팅을 조회하려면 `sys.getrefcount()`[^3]를 사용할 수 있습니다.
```python
def test_function():
    my_variable = ['a', 'b', 'c']
    print("my_variable in locals():", 'my_variable' in locals())
    print("my_variable in globals():", 'my_variable' in globals())
```

```shell
>>> import sys
>>> print(sys.getrefcount(test_function))
2
```

참조하는 개수는 1일 것 같지만 실제 `sys.getrefcount(test_function)`를 호출해보면 2가 출력됩니다. 이는 `getrefcount()`의 인수로 (임시) 참조가 포함되기 때문입니다.

그럼 다음으로 작은 숫자를 할당해보겠습니다.

```
>>> a = 1
>>> print(sys.getrefcount(a))
4294967295
```

파이썬에서는 자주 사용되는 작은 정수들을 미리 캐싱해두고 재사용합니다. 이를 "정수 인터닝(integer interning)"이라고 합니다.

파이썬에서는 `-5`부터 `256`까지의 정수들을 미리 생성해두고 필요할 때마다 같은 객체를 반환합니다. 따라서 이 범위 내의 정수들은 매우 높은 참조 개수를 가지게 됩니다. 실제로는 이 정수들의 참조 개수를 정확히 추적하지 않고, 대신 임의의 큰 값(4294967295)을 반환합니다.

#### 참조 카운트 감소시키기

`Py_DECREF` 는 객체의 참조 카운트를 감소시키는 역할을 합니다. 참조 카운트가 0이 되면 객체의 메모리를 해제합니다.
```c
static inline void _Py_DECREF(
#ifdef Py_REF_DEBUG
    const char *filename, int lineno,
#endif
    PyObject *op)
{
#ifdef Py_REF_DEBUG
    _Py_RefTotal--;
#endif
    if (--op->ob_refcnt != 0) {
#ifdef Py_REF_DEBUG
        if (op->ob_refcnt < 0) {
            _Py_NegativeRefcount(filename, lineno, op);
        }
#endif
    }
    else {
        _Py_Dealloc(op);
    }
}
```

-  `#ifdef Py_REF_DEBUG`와 `#endif` 사이의 코드는 디버그 모드에서만 컴파일됩니다.
- `_Py_RefTotal`은 전역 참조 카운트를 감소시킵니다.
-  `op->ob_refcnt`를 감소시킨 후, 그 값이 0이 아닌지 확인합니다.
    - 0이 아니라면, 아직 참조가 남아 있는 것이므로 메모리를 해제하지 않습니다.
    - 디버그 모드에서는 참조 카운트가 음수인지 확인하고, 음수라면 `_Py_NegativeRefcount`를 호출하여 오류를 보고합니다.
-  참조 카운트가 0이 되면 `_Py_Dealloc`을 호출하여 객체의 메모리를 해제합니다.

#### 바이트코드 연산에서의 참조 카운팅

다음 예제를 살펴보겠습니다.  `y`에 대한 참조가 몇 개일까요?

```python
import sys

y = "hello"

def greet(message=y):
    print(message.capitalize() + " " + y)

messages = [y]

greet(*messages)

print(sys.getrefcount(y))
```

위 코드를 실행하면 `y`에 대한 총 참조 수는 4개가 아니라 6개입니다.

- 1. `y = "hello"`: `y`가 문자열 객체를 참조합니다. 이 때 `STORE_NAME` 연산이 사용되며, 참조 카운트가 1 증가합니다.
- 2. `def greet(message=y)`: `y`가 `greet` 함수의 기본 인자로 사용됩니다. 이 때 `LOAD_NAME` 연산이 사용되며, 참조 카운트가 1 증가합니다.
- 3. `print(message.capitalize() + " " + y)`: `greet` 함수 내에서 `y`가 사용됩니다. 이 때 `LOAD_GLOBAL` 연산이 사용되며, 참조 카운트가 1 증가합니다.
- 4. `messages = [y]`: `y`가 리스트의 요소로 사용됩니다. 이 때 `BUILD_LIST` 연산이 사용되며, 참조 카운트가 1 증가합니다.
- 5. `greet(*messages)`: `greet` 함수를 호출할 때 `y`가 인자로 전달됩니다. 이 때 `CALL_FUNCTION` 연산이 사용되며, 참조 카운트가 1 증가합니다.
- 6. `print(sys.getrefcount(y))`: `sys.getrefcount(y)`를 호출할 때 `y`가 인자로 전달됩니다. 이 때 `LOAD_GLOBAL` 연산이 사용되며, 참조 카운트가 1 증가합니다.

연산을 예제로 살펴봅시다. 

```python
a = 10
b = 20
c = a * b
```

a, b를 선언하고 a, b를 곱한 값을 c에 할당한 식을 살펴봅시다. 세 번째 연산인 `c = a * b`는 세 가지 연산으로 나눌 수 있습니다.
- `LOAD_FAST`: a 변수를 확인하고 값 스택에 추가한 후 변수의 참조를 1 증가시킨다.
- `LOAD_FAST`: b 변수를 확인하고 값 스택에 추가한 후 변수의 참조를 1 증가시킨다.
- `BINARY_MULTIPLY`: 왼쪽 값에 오른 쪽 값을 곱하고 값 스택에 추가합니다.

`LOAD_FAST` 연산은 주어진 이름의 객체를 로드하고 값 스택(value stack)의 맨 위에 푸시한 다음 참조 수를 1 증가시킵니다. 값 스택은 바이트코드 연산의 피연산자와 연산 결과를 저장하는 데 사용됩니다.

`LOAD_FAST` 연산은 다음과 같이 구현되어 있습니다.

```c
case TARGET(LOAD_FAST): {
    PyObject *value = GETLOCAL(oparg);
    if (value == NULL) {
        format_exc_check_arg(tstate, PyExc_UnboundLocalError,
                             UNBOUNDLOCAL_ERROR_MSG,
                             PyTuple_GetItem(co->co_varnames, oparg));
        goto error;
    }
    Py_INCREF(value);
    PUSH(value);
    FAST_DISPATCH();
}
```

위 코드에서 `GETLOCAL(oparg)`는 주어진 인덱스(`oparg`)에 해당하는 로컬 변수를 가져옵니다. 변수의 값이 성공적으로 로드되면 `Py_INCREF(value)`를 호출하여 참조 카운트를 1 증가시키고, `PUSH(value)`를 통해 값 스택에 해당 값을 푸시합니다. `FAST_DISPATCH()`는 매크로로 인터프리터의 메인 루프에서 다음 바이트코드 명령어로 빠르게 이동하는 역할을 합니다.

`BINARY_MULTIPLY` 연산은 두 개의 피연산자를 값 스택에서 팝(pop)하고, 곱셈 연산을 수행한 후, 결과값을 다시 값 스택에 푸시합니다. 이 과정에서 피연산자들의 참조 카운트는 감소하게 됩니다.

```c
case TARGET(BINARY_MULTIPLY): {
    PyObject *right = POP();
    PyObject *left = TOP();
    PyObject *res = PyNumber_Multiply(left, right);
    Py_DECREF(left);
    Py_DECREF(right);
    SET_TOP(res);
    if (res == NULL)
        goto error;
    DISPATCH();
}
```

위 예에서 `POP()`과 `TOP()`을 통해 값 스택에서 피연산자들을 가져옵니다. `PyNumber_Multiply(left, right)`를 호출하여 곱셈 연산을 수행하고, 그 결과를 `res`에 저장합니다. 이후 `Py_DECREF(left)`와 `Py_DECREF(right)`를 호출하여 피연산자들의 참조 카운트를 감소시킵니다. 마지막으로 `SET_TOP(res)`를 통해 결과값을 값 스택의 맨 위에 설정합니다.

이처럼 바이트코드 연산에서는 객체의 참조 카운트를 적절히 증가시키고 감소시키는 작업이 이루어집니다. 하지만 이러한 작업이 올바르게 이루어지지 않으면 메모리 누수나 잘못된 메모리 접근 등의 문제가 발생할 수 있습니다.

#### 순환 참조와 가비지 컬렉션

참조 카운팅의 가장 큰 단점 중 하나는 순환 참조(circular reference)를 처리하지 못한다는 것입니다. 순환 참조는 객체들이 서로를 참조하고 있어 참조 카운트가 0이 되지 않는 상황을 말합니다.

```python
x = []
x.append(x)
del x
```

x는 스스로를 참조하고 있기 때문에 x의 참조 카운트는 0이 되지 않고 1로 유지됩니다.

이러한 문제를 해결하기 위해 CPython은 가비지 컬렉션(garbage collection) 메커니즘을 도입했습니다. 가비지 컬렉터는 주기적으로 실행되며, 참조 카운트가 0이 아니지만 도달할 수 없는(unreachable) 객체들을 찾아 메모리에서 해제합니다.

```python
import gc

gc.set_debug(gc.DEBUG_SAVEALL) # 순환 참조를 gc.garbage에 남깁니다.

x = []
x.append(x)
del x

print("Before gc.collect():")
for obj in gc.garbage:
    print(obj)

gc.collect() # 가비지 컬렉터 강제 실행

print("After gc.collect():")
for obj in gc.garbage:
    print(obj)
```

```shell
Before gc.collect():
After gc.collect():
[[...]]
```

- `gc.set_debug(gc.DEBUG_SAVEALL)`: 이 구문은 가비지 컬렉터 설정을 변경하여, 가비지 컬렉터가 회수한 모든 객체를 `gc.garbage` 리스트에 저장하도록 합니다. 이렇게 하면 순환 참조로 인해 회수된 객체들을 분석할 수 있습니다.
- `x = []`: 빈 리스트를 생성합니다.
-  `x.append(x)`: 리스트 `x`가 자신을 포함하도록 합니다. 이는 `x` 내부에 `x` 자신에 대한 참조를 만들어 순환 참조를 생성합니다.
-  `del x`: 변수 `x`에 대한 참조를 삭제합니다. 이 시점에서 `x`는 메모리에 남아 있지만, 직접적인 참조는 존재하지 않습니다. 순환 참조로 인해, 가비지 컬렉터만이 이를 처리할 수 있습니다.
- `gc.collect()`: 가비지 컬렉터를 강제로 실행하여 순환 참조를 포함한 미수거 객체들을 찾아내고 처리합니다. `gc.set_debug(gc.DEBUG_SAVEALL)` 설정으로 인해, 처리된 객체들은 `gc.garbage`에 저장됩니다.
-  `for obj in gc.garbage`: `gc.garbage`에 저장된 객체들을 순회하며 출력합니다. 이 경우, 자기 자신을 참조하는 리스트 `x`가 출력됩니다. 출력된 `[[...]]`는 리스트가 자기 자신을 참조하고 있음을 나타냅니다.

위 예제에서는 가비지 컬렉터를 실행하기 전에는 `gc.garbage`가 비어 있지만, 가비지 컬렉터 실행 후에는 순환 참조 객체가 `gc.garbage`에 수집되는 것을 보여줍니다.

### 요약

CPython의 메모리 관리 방식인 참조 카운팅에 대해 알아보았습니다. 참조 카운팅은 객체에 대한 참조 수를 추적하여 더 이상 사용되지 않는 객체를 자동으로 메모리에서 해제합니다.

- CPython은 C의 동적 메모리 할당 시스템을 기반으로 구축되어 있으며, 메모리 요구 사항은 런타임에 결정됩니다.
- Python 객체는 `PyObject` 구조체로 표현되며, 객체의 타입과 참조 카운트 등의 정보를 포함하고 있습니다.
- 참조 카운트는 `Py_INCREF()`와 `Py_DECREF()` 매크로를 통해 관리됩니다. 객체가 참조될 때마다 `Py_INCREF()`가 호출되어 참조 카운트가 증가하고, 참조가 해제될 때마다 `Py_DECREF()`가 호출되어 참조 카운트가 감소합니다.
- 참조 카운트가 0이 되면 객체는 더 이상 사용되지 않는 것으로 간주되어 메모리에서 해제됩니다.
- 참조 카운팅의 단점은 순환 참조를 처리하지 못한다는 것입니다. 이를 해결하기 위해 CPython은 가비지 컬렉션을 도입했습니다.
- 가비지 컬렉터는 주기적으로 실행되며, 참조 카운트가 0이 아니지만 도달할 수 없는 객체들을 찾아 메모리에서 해제합니다.

CPython의 메모리 관리는 참조 카운팅과 가비지 컬렉션이라는 두 가지 전략을 통해 이루어집니다. 이를 통해 개발자는 메모리 관리에 대해 크게 신경 쓰지 않고도 Python을 사용할 수 있습니다. 하지만 메모리 누수나 순환 참조 등의 문제를 완전히 방지하기 위해서는 메모리 관리 방식에 대한 이해가 필요합니다.

## References
- [^1]: https://docs.python.org/3/c-api/refcounting.html
- [^2]: https://devguide.python.org/garbage_collector/#garbage-collection
- [^3]: https://docs.python.org/3/library/sys.html#sys.getrefcount
