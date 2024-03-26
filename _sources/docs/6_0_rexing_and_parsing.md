# 6. 렉싱과 파싱
- [렉싱과 파싱](#렉싱과-파싱)
  - [6.0 개요](#60-개요)
  - [6.1 CST 생성](#61-cst-생성)
  - [6.2 파서 \& 토크나이저](#62-파서--토크나이저)
  - [6.3 추상 구문 트리](#63-추상-구문-트리)
  - [6.4 정리](#64-정리)

<br/>
<br/>
<br/>

## 6.0 개요
파이썬은 문법을 해석하기 위해서 CST(Concrete syntax tree) 와 AST(Abstract syntax tree) 두 가지 구조를 사용합니다. CST 와 AST 2단계를 통해서 문법을 파싱하게 되는데, 이번 챕터를 통해서 CST 와 AST 를 살펴보겠습니다.
<br/>


![parse_tree](../images/6_rexing/01_parse_tree.png)  

<br/>
<br/>
<br/>


## 6.1 CST 생성
파스 트리라고도 부르는 CST 는 작성한 코드를 루트와 순서가 있는 트리구조로 바꾸는 일련의 작업을 의미합니다. 다음은 CST 구문을 사용하여 a + 1 을 산술표현식으로 표현한 예입니다.


![CST_EXPR](../images/6_rexing/00_CST_EXPR.jpg)

<br/>
<br/>
<br/>

CST 를 구성하는 문법은 Grammar 폴더의 Grammar 에서 정의하며, arith_expr, term, factor, power 등 여러 심볼들이 존재합니다. 또한 흔히 말하는 토큰은 Grammar 폴더의 Tokens 에서 정의하고 있으며,NAME 토큰은 변수나 함수, 클래스 모듈의 이름을 표현합니다.


![Parsing_Name](../images/6_rexing/03_Parsing_Name.jpg)

<br/>
<br/>
<br/>


## 6.2 파서 & 토크나이저
C-Python의 파서-토크나이저를 통해서, CST 의 골격 구조를 완성할 수 있는데, 다음과 같이 파서-토크나이저를 통해 연속적인 CST 트리 구조를 완성할 수 있습니다.


![Parser_Tokenizer](../images/6_rexing/02_Parser_Tokenizer.jpg)

<br/>
<br/>
<br/>

파서 토크나이저는 PyParser_ASTFromFileObject() 를 통해서 파서의 진입점을 찾을 수 있습니다.PyParser_ASTFromFileObject( ) 은 다음 두 단계를 거쳐 CST -> AST 파싱을 진행합니다.
1. PyParser_ParserFileObject() 를 통해 CST 로 변환.
2. PyAST_FromNodeObject() 를 사용해 CST 를 AST 로 변환.

하게 됩니다.

:sparkles: 저와 같은 경우, 파이썬 3.9 에서 PyParser_ASTFromFileObject() 가 중단점이 걸리지 않아 확인해 보니, PEG 옵션을 켜두어 *_use_peg_parser* 를 꺼놓고 진행했습니다.

<br/>
<br/>
<br/>

## 6.3 추상 구문 트리
*추상 구문 트리 단계*는 CST 로 변환한 트리를 좀 더 논리적인 구조로 변환하는 단계입니다. CST는 코드 파일의 텍트를 있는 그대로 표현하는 구조로 텍스트로부터 토큰을 추출하여, 토큰 종류만 구분해 둔 상태에 불과합니다.(즉 CST 로 기본적인 문법 구조를 알 수 있지만, 함수, 스코프, 루프 등등 상세한 정보를 파악하기는 힘들다고 합니다..) 따라서 코드를 컴파일하기 전에 CST 를 실제 파이썬 언어 구조와 의미 요소를 표현하는 고수준 구조인 AST 로 변환해야 합니다.

다음은 AST 와 관련된 소스파일 목록입니다.
1. Include -> python-ast.h
2. Parser -> Python.asdl
3. Python -> ast.c

ast 모듈은 문법을 다시 생성할 때, Python-ast.h 를 임포트하게 된느데, 이 파일은 Parser->Python.asdl 에서 다시 생성되게 됩니다. 즉 Include -> python-ast.h의 파라미터와 이름은 Parser->python.asdl 의 정의를 따르도록 재생성 됩니다.

그 후, AST 의 진입점인 PyAST_FromNodeObject( ) 는 TYPE(n) 에 대한 switch 문을 실행하고, 결과로 심벌 또는 토큰 타입을 반환하게 됩니다.

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