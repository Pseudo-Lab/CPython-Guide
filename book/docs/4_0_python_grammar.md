# 4. 파이썬 언어와 문법

- 파이썬 애플리케이션은 보통 소스 코드 형태로 배포됩니다.
- 소스 코드를 바이트코드라는 중간 언어로 컴파일하고 → `.pyc` 파일에 저장 + 실행 위해 캐싱을 진행합니다.
- 파이썬 인터프리터가 해당 바이트코드(`.pyc`)를 한 줄씩 읽고 실행합니다.
    - CPython 런타임이 첫 번째 실행될 때 코드를 컴파일하지만, 일반 사용자에게 노출되지는 않습니다.
    - 코드 변경 없이 같은 파이썬 애플리케이션 다시 실행하면 → 컴파일된 바이트코드를 불러와서 더 빠르게 실행합니다.

<details>
<summary>💡 이식성(portability)을 기준으로 컴파일러를 선택한다면..</summary>

- 저수준 기계어
    - 시스템에서 바로 실행할 수 있는 기계어로 컴파일
    - 바이러니 실행 파일로 컴파일 → 컴파일한 플랫폼과 동일한 플랫폼에서 사용 가능
    - ex) C, Go, C++, Pascal
- 중간 언어
    - 가상 머신에서 실행하기 위한 언어로 컴파일
    - 여러 시스템 아키텍처에서 사용 가능한 중간 언어로 컴파일
    - ex) 닷넷 CLR, JAVA, **Python**
</details>


## 4.1 CPython이 파이썬이 아니라 C로 작성된 이유

<details>
<summary>결론 먼저 보기</summary>

- CPython은 파이썬에서 이용하는 많은 라이브러리가 C로 되어있기 때문에 C로 만들어진 컴파일러를 사용합니다.
- 안정적인 언어로 다양한 표준 라이브러리 모듈을 이용하기 위해서 C 컴파일러를 사용하고 있습니다.

</details><br>

- 새로운 프로그래밍 언어를 만들려면 한 언어(source language)를 다른 만들고자 하는 언어(target language)로 바꿔줄 컴파일러가 필요합니다.
- 새로운 언어 개발 시 어떤 프로그램이든 실행할 수 있어야 하기 때문에 보통 **더 오래되고 안정적인 언어**로 컴파일러를 작성합니다.

> 💡 <b>컴파일러 유형</b>
> - 셀프 호스팅 컴파일러
>     - 자기 자신으로 작성한 컴파일러 (부트스트래핑 단계를 통해 만들어짐)
>     - ex) Go(C로 작성된 첫번째 Go 컴파일러가 Go를 컴파일할 수 있게 되자 → 컴파일러를 Go로 재작성), PyPy(파이썬으로 작성된 파이썬 컴파일러)
> - 소스 대 소스(source-to-source) 컴파일러
>     - 이미 갖고 있는 다른 언어로 작성한 컴파일러
>     - ex) CPython (C → Python)

- 여러 표준 라이브러리 모듈(ssl, sockets 등)도 저수준 운영체제 API에 접근하기 위해서 C로 작성되어 있고,
<br>네트워크 소켓 만들기, 파일 시스템 조작, 디스플레이와 상호작용하는 윈도우/리눅스 커널 API도 모두 C로 작성되어 있기 때문에 **파이썬 또한 확장성을 고려하여 C로 작성되었다**고 볼 수 있습니다.



## 4.2 파이썬 언어 사양
- 컴파일러가 언어를 실행하기 위해서는 문법 구조에 대한 엄격한 규칙인 **언어 사양**이 필요합니다.
([CPython 배포판 구성 요소](https://www.notion.so/CPython-4ee3a6e7bfff48d8b1b54c8aced084a8?pvs=21) 참고)
- 언어 사양은 모든 파이썬 인터프리터 구현이 사용하는 레퍼런스 사양으로,
    - 사람이 읽을 수 있는 형식 + 기계가 읽을 수 있는 형식으로 제공합니다.
    - 문법 형식 + 각 문법 요소가 실행되는 방식을 자세히 설명하고 있습니다.

### 언어 레퍼런스
사람이 읽을 수 있는 형식으로, Doc/reference에 언어의 구조, 키워드를 정의해두고 있습니다.
```bash
Doc/reference
├── index.rst               # 언어 레퍼런스 목차
├── introduction.rst        # 레퍼런스 문서 개요
├── compound_stmts.rst      # 복합문 (if, while, for, 함수 정의 등)
├── datamodel.rst           # 객체, 값, 타입
├── executionmodel.rst      # 프로그램 구조
├── expressions.rst         # 표현식 구성 요소
├── grammar.rst             # 문법 규격(Grammar/Grammar 참조)
├── import.rst              # import 시스템
├── lexical_analysis.rst    # 어휘 구조 (줄, 들여쓰기, 토큰, 키워드 등)
├── simple_stmts.rst        # 단순문 (assert, import, return, yield 등)
└── toplevel_components.rst # 스크립트 및 모듈 실행 방법 설명
```
<details>
<summary>ex1) if (compound_stmts.rst)</summary>
    
```markdown
.. _if:
.. _elif:
.. _else:

The :keyword:`!if` statement
============================

.. index::
    ! statement: if
    keyword: elif
    keyword: else
    single: : (colon); compound statement

The :keyword:`if` statement is used for conditional execution:

.. productionlist:: python-grammar
    if_stmt: "if" `assignment_expression` ":" `suite`
            : ("elif" `assignment_expression` ":" `suite`)*
            : ["else" ":" `suite`]

It selects exactly one of the suites by evaluating the expressions one by one
until one is found to be true (see section :ref:`booleans` for the definition of
true and false); then that suite is executed (and no other part of the
:keyword:`if` statement is executed or evaluated).  If all expressions are
false, the suite of the :keyword:`else` clause, if present, is executed.
```

</details>

<details>
<summary>ex2) Class instance (datamodel.rst)</summary>

```markdown
Class instances
    .. index::
        object: class instance
        object: instance
        pair: class; instance
        pair: class instance; attribute

    A class instance is created by calling a class object (see above).  A class
    instance has a namespace implemented as a dictionary which is the first place
    in which attribute references are searched.  When an attribute is not found
    there, and the instance's class has an attribute by that name, the search
    continues with the class attributes.  If a class attribute is found that is a
    user-defined function object, it is transformed into an instance method
    object whose :attr:`__self__` attribute is the instance.  Static method and
    class method objects are also transformed; see above under "Classes".  See
    section :ref:`descriptors` for another way in which attributes of a class
    retrieved via its instances may differ from the objects actually stored in
    the class's :attr:`~object.__dict__`.  If no class attribute is found, and the
    object's class has a :meth:`~object.__getattr__` method, that is called to satisfy
    the lookup.

    .. index:: triple: class instance; attribute; assignment

    Attribute assignments and deletions update the instance's dictionary, never a
    class's dictionary.  If the class has a :meth:`~object.__setattr__` or
    :meth:`~object.__delattr__` method, this is called instead of updating the instance
    dictionary directly.

    .. index::
        object: numeric
        object: sequence
        object: mapping

    Class instances can pretend to be numbers, sequences, or mappings if they have
    methods with certain special names.  See section :ref:`specialnames`.

    .. index::
        single: __dict__ (instance attribute)
        single: __class__ (instance attribute)

    Special attributes: :attr:`~object.__dict__` is the attribute dictionary;
    :attr:`~instance.__class__` is the instance's class.
```

</details>


### 문법
기계가 읽을 수 있는 형식으로, Grammar/python.gram에 PEG 표현식을 통해 정의하고 있습니다.

- 파서 표현식 문법(parsing expression grammar, PEG) 사양
    - `*`: 반복
    - `+`: 최소 1번 반복
    - `[]`: 선택적인 부분
    - `|`: 대안
    - `()`: 그룹
<details>
<summary>ex0) 커피 레시피</summary>
- 예시
    - 컵 필요: `'cup'`
    - 최소 에스프레소 한 샷 이상: `('espresso')+`
    - 물 사용 (옵션): `['water']`
    - 우유 사용 (옵션): `[milk]`
    - 우유 사용했다면, 탈지우유나 두유 등 여러 종류의 우유 선택 가능: `milk: 'full-fat' | 'skimmed' | 'soy'`
- 정의
    
    ```makefile
    coffee: 'cup' ('espresso')+ ['water'] [milk]
    milk: 'full-fat' | 'skimmed' | 'soy'
    ```
    
- 철도 다이어그램
    
    ![Untitled](Chapter%203-4%20%E1%84%8F%E1%85%A5%E1%86%B7%E1%84%91%E1%85%A1%E1%84%8B%E1%85%B5%E1%86%AF%E1%84%92%E1%85%A1%E1%84%80%E1%85%B5%20%E1%84%8B%E1%85%A5%E1%86%AB%E1%84%8B%E1%85%A5%E1%84%8B%E1%85%AA%20%E1%84%86%E1%85%AE%E1%86%AB%E1%84%87%E1%85%A5%E1%86%B8%20ccf77bc99a5b48c29fbc06230785b99b/Untitled%201.png)

</details>

<details>
<summary>ex1) while문</summary>
- 예시
    1. 표현식 & `:` 단말 기호 & 코드 블록으로 구성
        
        ```python
        while finished:
                do_things()
        ```
        
    2. named_expression 대입 표현식 사용 (값 할당하는 동시에 그 값을 평가하는 표현식)
        
        ```python
        while letters := read(document, 10):
                print(letters)
        ```
        
    3. while문 다음에 else 블록 사용
        
        ```python
        while item := next(iterable):
                print(item)
        else:
                print("Iterable is empty")
        ```
        
- 정의 (while_stmt 문법 파일)
    
    ```python
    # Grammar/python.gram#L165
    
    while_stmt[stmt_ty]:
            | 'while' a=named_expression ':' b=block c=[else_block] ...
    ```
    
- 철도 다이어그램
    
    ![Untitled](Chapter%203-4%20%E1%84%8F%E1%85%A5%E1%86%B7%E1%84%91%E1%85%A1%E1%84%8B%E1%85%B5%E1%86%AF%E1%84%92%E1%85%A1%E1%84%80%E1%85%B5%20%E1%84%8B%E1%85%A5%E1%86%AB%E1%84%8B%E1%85%A5%E1%84%8B%E1%85%AA%20%E1%84%86%E1%85%AE%E1%86%AB%E1%84%87%E1%85%A5%E1%86%B8%20ccf77bc99a5b48c29fbc06230785b99b/Untitled.jpeg)

</details>

<details>
<summary>ex2) try문</summary>
- 정의
    
    ```python
    # Grammar/python.gram#L189
    
    try_stmt[stmt_ty]:
        | 'try' ':' b=block f=finally_block { _Py_Try(b, NULL, NULL, f, EXTRA) }
        | 'try' ':' b=block ex=except_block+ el=[else_block] f=[finally_block] { _Py_Try(b, ex, el, f, EXTRA) }
    
    finally_block[asdl_seq*]: 'finally' ':' a=block { a }
    
    except_block[excepthandler_ty]:
        | 'except' e=expression t=['as' z=NAME { z }] ':' b=block {
            _Py_ExceptHandler(e, (t) ? ((expr_ty) t)->v.Name.id : NULL, b, EXTRA) }
        | 'except' ':' b=block { _Py_ExceptHandler(NULL, NULL, b, EXTRA) }
    
    else_block[asdl_seq*]: 'else' ':' b=block { b }
    ```
    
- 철도 다이어그램
    
    ![Untitled](Chapter%203-4%20%E1%84%8F%E1%85%A5%E1%86%B7%E1%84%91%E1%85%A1%E1%84%8B%E1%85%B5%E1%86%AF%E1%84%92%E1%85%A1%E1%84%80%E1%85%B5%20%E1%84%8B%E1%85%A5%E1%86%AB%E1%84%8B%E1%85%A5%E1%84%8B%E1%85%AA%20%E1%84%86%E1%85%AE%E1%86%AB%E1%84%87%E1%85%A5%E1%86%B8%20ccf77bc99a5b48c29fbc06230785b99b/Untitled%202.png)

</details>

eg)
coffee: 'cup' ('espresso') + \['water'\] \[milk\]

milk: 'full-fat' | 'skimmed' | 'soy'

철도 다이어그램
![철도 다이어그램](../images/4_grammar/train_diagram.svg)  

### Parser
Grammar/python.gram에 파이썬 문법이 PEG로 정의가 되어있다

![small_stmt 예시](../images/4_grammar/small_stmt.png)

```
'pass' { _Py_Pass(EXTRA) }
```

줄을


```
('pass'|'proceed') { _Py_Pass(EXTRA) }
```

로 바꾸고 컴파일 하면,

proceed라는 함수가 pass랑 동일한 action을 하게 된다

```
def test1():
    pass

def test2():
    proceed
```

위에서 test1()이랑 test2()의 action은 동일하다.

python.gram파일 수정을 통해서 파이썬 문법을 변경할 수 있다

## 4.4 토큰
Grammar/Tokens 파일은 파스 트리의 Leaf node에서 사용되는 고유 토큰들을 정의한다. 코드 tokenization은 추후에 compiling할때 이용된다.

![tokens 예시](../images/4_grammar/tokens.png)

python코드가 tokenizer를 통해서 토큰으로 파싱이 된다. 위 코드를 tokenize를 하면:

![코드 token화 예시](../images/4_grammar/code_tokenized.png)
