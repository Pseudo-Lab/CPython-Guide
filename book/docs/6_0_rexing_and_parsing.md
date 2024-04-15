# 6. 렉싱과 파싱
- [렉싱과 파싱](#렉싱과-파싱)
  - [6.0 개요](#60-개요)
  - [6.1 CST 생성](#61-cst-생성)
  - [6.2 파서 \& 토크나이저](#62-파서--토크나이저)
  - [6.3 추상 구문 트리](#63-추상-구문-트리)
  - [6.4 정리](#64-정리)


## 6.0 개요
> *저번 시간에는 CPython 런타임 구성과 명령줄 문자열, 로컬 모듈, 스크립트 파일, 컴파일된 바이트 코드가 입력으로 들어왔을 때 CPython에서 어떻게 처리하는지 살펴보았습니다.<br/>
이번 시간에는 입력 받은 코드를 컴파일 가능한 논리적 구조로 만들어 주는 렉싱과 파싱에 대해 알아봅니다.*

파이썬은 문법을 해석하기 위해서 CST(Concrete syntax tree) 와 AST(Abstract syntax tree) 두 가지 구조를 사용하며, 각각 렉서와 파서에 의해 만들어집니다.
<br/>

![input_to_compiler](../images/6_rexing/04_Input_to_Compiler.png)
<!-- <p align="center"><img src="book/images/6_rexing/04_Input_to_Compiler.png" height="100px" width="300px"></p> -->

##### **출처: https://medium.com/@codeinseoul/python-lexer-and-parser-d0dbe676a6e*
<br/>

![parse_tree](../images/6_rexing/01_parse_tree.png)
- CST : 토큰과 심벌에 대한 **문맥(context)이 없는** 트리 집합
- AST : 파이썬 문법과 문장들에 대한 **문맥(context)이 있는** 트리 집합

잠깐! 책에서 '렉서'와 '파서+토크나이저' 두 용어를 혼용하고 있습니다. 이를테면 CST를 생성하는 건 렉서 혹은 파서+토크나이저라고 하는 식입니다. 그렇다면 두 용어는 동일한 뜻을 가진 단어일까요?
#### 🤔 파서+토크나이저 = 렉서?
```text
세 용어 모두 "컴파일러 이론 용어"입니다.

•Tokenizer: 구문에서 의미있는 요소들을 토큰으로 쪼갬
•Lexer: 토큰의 의미를 분석
•Parser: Lexical analyze 된 후 토큰화된 데이터를 CST라는 구조로 표현

*Lexical analyze?
•Tokenizer를 거치며 의미있는 단위로 쪼개지고, Lexer를 거치며 그 결과의 의미를 분석하는 과정

ex) return 명령어 분석
- return 이라는 단어에서 r, e, t, u, r, n 은 각각 따로놓고 보면 아무 의미도 가지지 않음
- Tokenizer 를 거치며 return 이라는 의미있는 단어가 됨 -> 토큰화
- Lexer 를 거치며 이 토큰은 무언가를 반환하라는 명령어구나! 라고 의미를 분석함
- 해당 토큰은 {type: 명령어, value: "return", child: []} 와 같은 식으로 의미가 분석되어 Parser 에게 전달됨
```
[References]
👉🏻[용어 정의, 사진](https://velog.io/@mu1616/%EC%BB%B4%ED%8C%8C%EC%9D%BC%EB%9F%AC-%EC%9D%B4%EB%A1%A0%EC%97%90%EC%84%9C-%ED%86%A0%ED%81%AC%EB%82%98%EC%9D%B4%EC%A0%80Tokenizer-%EB%A0%89%EC%84%9CLexer-%ED%8C%8C%EC%84%9CParse-%EC%9D%98-%EC%97%AD%ED%95%A0)
👉🏻[return 명령어 예시](https://trumanfromkorea.tistory.com/79)

- 결론: **원칙적으로 파서+토크나이저가 곧 렉서는 아닙니다.** 다만 **렉서, 즉 토큰의 의미를 분석하는 기능의 구현은 언어마다 다르며,** CPython의 렉서는 파서와 토크나이저를 합친 형태로 되어 있다고 이해하면 될 것 같습니다.

<br/>
<br/>
<br/>


## 6.1 CST 생성
파스 트리라고도 부르는 CST 는 작성한 코드를 루트와 순서가 있는 트리로 변환한 결과물입니다. 다음은  a + 1라는 산술식이 CST로 표현된 모습입니다.<br/>
![CST_EXPR](../images/6_rexing/00_CST_EXPR.jpg)
<br/>

파서는 입력 스트림으로 들어오는 토큰들이 파이썬 문법에 맞는 토큰인지 검증하는 동시에 CST를 생성합니다. 검증에는 Grammar 폴더 내 Grammar 파일에 정의돼있는 심볼들을 사용하며, 심볼은 CST 를 구성하는 노드가 됩니다.

아래 사진을 통해 Grammar 파일에 정의된 arith_expr, term, factor, power 등의 심볼이 CST 노드에 대응한다는 사실을 확인할 수 있습니다.
![Grammar_Grammar](../images/6_rexing/05_Grammar_Grammar.png)
<br/>

또한 <4. 파이썬 언어와 문법>(p.48)에서 나왔던 것처럼, 토큰은 Grammar 폴더의 Tokens 에서 정의하고 있습니다. 이번 시간에는 NAME과 NUMBER 토큰을 예시로 들겠습니다.<br/>
• NAME 토큰은 변수나 함수, 클래스 모듈의 이름을 표현합니다.
• NUMBER 토큰은 다양한 숫자 형식 값을 표현합니다. 이를테면 '0b10000'로 표현된 숫자를 이진수라고 이해하는데 쓰일 수 있습니다.
![Parsing_Name](../images/6_rexing/03_Parsing_Name.jpg)
이 때 python의 symbol과 token 모듈로 컴파일된 심벌과 토큰을 확인할 수 있습니다.
<br/>
<br/>
<br/>


## 6.2 파서-토크나이저
### 6.2.1 연관된 소스 파일 목록

| 파일                 | 설명                                               |
| ------------------ | ------------------------------------------------ |
| Python/pythonrun.c | 파서와 컴파일러 실행                                      |
| Parser/parsetok.c  | 파서와 토크나이저 구현                                     |
| Parser/tokenizer.c | 토크나이저 구현                                         |
| Parser/tokenizer.h | 토큰 상태 등의 데이터 모델을 정의하는 토크나이저 구현 헤더 파일             |
| Include/token.h    | Tools▶︎scripts▶︎generate_token.py에 의해 생성되는 토큰 정의 |
| Include/node.h     | 토크나이저를 위한 CST 노드 인터페이스와 매크로                      |
<br/>
<br/>



### 6.2.2. 파일 데이터를 파서에 입력하기
파서-토크나이저는 PyParser_ASTFromFileObject() 를 통해 파서의 진입점을 찾을 수 있습니다. PyParser_ASTFromFileObject() 은 다음 두 단계를 거쳐 CST -> AST 파싱을 진행합니다.
1. PyParser_ParseFileObject() 를 통해 CST 로 변환
2. PyAST_FromNodeObject() 를 사용해 CST 를 AST 로 변환<br>

PyParser_ParseFileObject() 함수는 2가지 중요한 작업을 수행합니다.<br/>

1. PyTokenizer_FromFile()을 사용해 토크나이저 상태 tok_state를 초기화<br/>
2. parsetok()를 사용해 토큰들을 CST(노드 리스트)로 변환 (Parser/parsetok.c L456:463)
```c
done:
    PyTokenizer_Free(tok);

    if (n != NULL) {
        _PyNode_FinalizeEndPos(n);
    }
    return n;
}
...
```
<br/><br/>

### 6.2.3 파서-토크나이저 흐름
기본적으로 커서가 텍스트 입력 끝에 도달하거나 문법 오류가 발견될 때까지 파서와 토크나이저를 실행합니다 (Parser/parsetok.c L242:253).
```c
#endif

    for (;;) {
        const char *a, *b;
        int type;
        size_t len;
        char *str;
        col_offset = -1;
        int lineno;
        const char *line_start;

        type = PyTokenizer_Get(tok, &a, &b);
        ...
```
<br/>

1) 본격적인 파서-토크나이저 실행 전, 토크나이저에서 사용하는 모든 상태를 저장하는 임시 데이터 구조인 tok_state를 초기화합니다 (Parser/parsetok.c L165:189).
```c
node *
PyParser_ParseFileObject(FILE *fp, PyObject *filename,
                         const char *enc, grammar *g, int start,
                         const char *ps1, const char *ps2,
                         perrdetail *err_ret, int *flags)
                         {
    struct tok_state *tok;
    ...
    if ((tok = PyTokenizer_FromFile(fp, enc, ps1, ps2)) == NULL) {
            err_ret->error = E_NOMEM;
            return NULL;
        }
        if (*flags & PyPARSE_TYPE_COMMENTS) {
            tok->type_comments = 1;
        }
        Py_INCREF(err_ret->filename);
        tok->filename = err_ret->filename;
        return parsetok(tok, g, start, err_ret, flags);
```
코드에서 볼 수 있듯, tok_state는 커서의 현재 위치와 같은 정보를 저장합니다.<br/>

2) tok_get()으로 다음 토큰을 얻고, 해당 토큰의 고유 ID를 파서로 전달합니다 (Parser/tokenizer.c L1171:1185).
```c
/* Get next token, after space stripping etc. */

static int
tok_get(struct tok_state *tok, const char **p_start, const char **p_end)
{
    int c;
    int blankline, nonascii;

    *p_start = *p_end = NULL;
  nextline:
    tok->start = NULL;
    blankline = 0;

    /* Get indentation level */
    if (tok->atbol) {
    ...
  return PyToken_OneChar(c);
}
```

3) 파서는 파서 생성기 오토마타(DFA)로 CST에 노드를 추가합니다 (Parser/parser.c L232:316).
```c
PyParser_AddToken(parser_state *ps, int type, char *str,
                  int lineno, int col_offset,
                  int end_lineno, int end_col_offset,
                  int *expected_ret)
{
  ...
  const dfa *d1 = PyGrammar_FindDFA(ps->p_grammar, nt);
  if ((err = push(&ps->p_stack, nt, d1,
                        arrow, lineno, col_offset,
                        end_lineno, end_col_offset)) > 0) {
                        D(printf(" MemError: push\n"));
                        return err;
                    }
                    D(printf(" Push '%s'\n", d1->d_name));
                    continue;
  ...
  return E_OK;
}

```

전 과정을 도식화하면 아래와 같습니다.
![Parser_Tokenizer](../images/6_rexing/02_Parser_Tokenizer.jpg)
<br/><br/><br/>


## 6.3 추상 구문 트리
*추상 구문 트리 단계*는 CST를 실행 가능한 형태이면서 좀더 논리적인 구조로 변환하는 단계입니다. CST는 코드 파일의 텍스트를 있는 그대로 표현한 구조로, 텍스트로부터 토큰을 추출하여 토큰 종류만 구분해 둔 상태에 불과합니다. 때문에 기본적인 문법 구조는 알 수 있지만 함수, 스코프, 루프 등 상세 정보는 파악이 불가능합니다.
따라서 코드를 컴파일하기 전에 파이썬 언어 구조와 의미 요소를 표현하는 AST 로 변환해야 합니다.<br/>

AST는 CPython 파싱 과정 중 생성하지만 표준 라이브러리의 ast 모듈을 사용해 생성할 수도 있습니다.<br/>

AST의 상세 구현을 보기 전에 파이썬 코드의 기본 요소들이 AST로 어떻게 표현되는지 알아봅시다.<br/>

### 6.3.1 AST 관련 소스 파일 목록

| 파일                    | 용도                                                                              |
| --------------------- | ------------------------------------------------------------------------------- |
| Include▶︎python-ast.h | Parser▶︎asdl_c.py로 생성한 AST 노드 타입 선언                                             |
| Parser▶︎Python.asdl   | 도메인 특화 언어인 ASDL(Abstract Syntax Description Language)5로 작성된 AST 노드 타입들과 프로퍼티 목록 |
| Python▶︎ast.c         | AST 구현                                                                          |
> python-ast.h 파일은 Parser▶︎Python.asdl 에서 재생성되며, python ast 모듈이 문법을 재생성할 때 불러와 사용합니다. 때문에 Include▶︎python-ast.h의 파라미터와 이름은 Parser▶︎Python.asdl의 정의를 따릅니다. 그 후 AST 의 진입점인 PyAST_FromNodeObject( ) 는 TYPE(n) 에 대한 switch 문을 실행하고, 결과로 심벌 또는 토큰을 반환합니다.

<br/>
<br/>
<br/>

## 6.4 정리 
- AST : 파이썬 문법과 문장들에 대한 *문맥*(context) 있는* 트리 집합.
- CST : 토큰과 심벌에 대한 *문맥(context)이 없는* 트리 집합
- 토큰 : 심벌의 종류 중 하나.
- 토큰화 : 텍스트를 토큰들로 변환하는 과정이다.
- 파싱 : 텍스트를 CST 나 AST 로 변환하는 과정이다.


<br/>
<br/>
<br/>