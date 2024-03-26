# 1. CPython 살펴보기

> 앞으로 저희는 CPython에 대해 아래 내용을 다루게 됩니다 🚀
> - **CPython 소스 코드 읽고 탐색 / 컴파일**하기
> - Python 문법 수정하고 컴파일해서 자신만의 CPython 버전 만들기
> - list, dictionary, generator 등의 **내부 작동 방식 이해**하기
> - CPython **메모리 관리 기능** 이해하기
> - **병렬성과 동시성**을 통해 Python 코드 확장하기
> - 코어 타입에 새로운 기능 추가하기
> - **테스트 스위트** 실행하기
> - Python **코드와 런타임 성능을 프로파일하고 벤치마크**하기
> - C 코드와 Python 코드를 전문가처럼 **디버깅**하기
> - CPython 라이브러리의 구성 요소를 수정하거나 개선해서 **향후 CPython에 기여**하기

## 1.1 CPython이란?

- Python 구현체 중 하나로, 일반적으로 이용하는 [python.org](http://python.org) 에서 제공하는 공식 파이썬 구현체입니다.
- 이름에서 알 수 있듯이, CPython은 C로 구현되어 있습니다.
- 다른 python 구현체
    - Jython
        - Java로 작성된 파이썬 구현체
        - JVM(Java Virtual Machine)에서 실행
    - IronPython
        - C#로 작성된 파이썬 구현체
        - .NET 프레임워크 사용
    - PyPy
        - Python 정적 타입으로 작성된 파이썬 구현체
        <br>(정적 타입: 실행하기 전에 변수의 type을 미리 결정하고, 그 이후에는 type을 변경하지 않는 방식)
        - JIT(Just-In-Time: 프로그램을 실행하는 동안 실시간으로 기계어로 변환) 컴파일러 방식으로 구현되어 기존 interpreter 방식보다 빠르고 효율적

## 1.2 CPython 배포판 구성 요소

- **언어 사양(Language Specification)**: 파이썬 언어의 문법, 구문, 의미론
    - ex) `[]`: 인덱싱, 슬라이싱, 빈 리스트 생성을 위해 사용
- **컴파일러(Interpreter)**: C 언어로 작성된 컴파일러
    - 파이썬 소스 코드 → 실행 가능한 기계어로 변환하는 역할
- **표준 라이브러리 모듈(Standard Library Modules)**: 기본적으로 포함되어 있는 패키지
    - ex) 파일 입출력, 네트워킹, 문자열 처리, 데이터 구조, GUI 프로그래밍 등
- **코어 타입(Core Types)**: 내장 데이터 type
    - ex) 숫자, 문자열, list, tuple, dictionary
- **테스트 스위트(Test Suite)**: 개발 및 유지 보수에 사용되는 테스트 모음
    - ex) 유닛 테스트, 통합 테스트, 성능 테스트

## 1.3 소스 코드 들여다보기

- 소스 코드 다운로드 (3.9 버전을 기준으로 살펴볼 예정입니다.)
    ```bash
    git clone --branch 3.9 https://github.com/python/cpython
    ```
- 소스 코드 구성
    ```bash
    cpython
    ├── CODE_OF_CONDUCT.md
    ├── Doc        # 문서 소스 파일
    ├── Grammar    # 컴퓨터가 읽을 수 있는 언어 정의
    ├── Include    # C 헤더 파일
    ├── LICENSE
    ├── Lib        # 파이썬으로 작성된 표준 라이브러리 모듈
    ├── Mac        # macOS를 위한 파일
    ├── Makefile.pre.in
    ├── Misc       # 기타 파일
    ├── Modules    # C로 작성된 표준 라이브러리 모듈
    ├── Objects    # 코어 타입과 객체 모델
    ├── PC         # 이전 버전의 윈도우를 위한 윈도우 빌드 지원 파일
    ├── PCbuild    # 윈도우 빌드 지원 파일
    ├── Parser     # 파이썬 파서 소스 코드
    ├── Programs   # python 실행 파일과 기타 바이너리를 위한 소스 코드
    ├── Python     # CPython 인터프리터 소스 코드
    ├── README.rst
    ├── Tools      # CPython 빌드하거나 확장하는 데 유용한 독립 실행형 도구
    ├── aclocal.m4
    ├── config.guess
    ├── config.sub
    ├── configure
    ├── configure.ac
    ├── install-sh
    ├── pyconfig.h.in
    └── setup.py
    ```
