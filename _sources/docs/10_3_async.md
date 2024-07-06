# 비동기 프로그래밍

## 1. 비동기 프로그래밍

- 파이썬은 스레드와 멀티프로세싱을 사용하지 않는 동시성 프로그래밍 방법 또한 제공함
- 발전하며 버전에 따라 추가, 개선, 폐지된 사항들이 존재
    - Python 3.9
        - `@coroutine` 폐지
        - `async` 키워드로 퓨처 생성 가능
        - `yield from` 키워드로 코루틴 실행 가능
- 제너레이터
- 코루틴
- 비동기 제너레이터
- 서브 인터프리터

## 2. 제너레이터

- 제너레이터
    - `yield` 문으로 값을 반환하고 재개되어 값을 추가로 반환할 수 있는 함수
    - `yield` 문을 통해 값을 하나씩 생성하여 반환하고, 호출될 때마다 이전 상태를 유지하며 실행을 재개하는 함수
    - `yield` : 현재 값 반환 + 함수 실행 중단
- 예시
    
    ```python
    def letters():
        i = 97
        end = 97 + 26
        while i < end:
            yield chr(i)
            i += 1
    
    for letter in letters():
        print(letter)
    ```
    
- 파일, DB, 네트워크 같은 큰 데이터 블록의 값을 순회할 때 메모리 효율 측면에서 유리함
    - `return` 문의 경우 반환된 값이 그때그때 메모리에 올라감
    - `yield` 문의 경우 우선 제너레이터 객체가 생성되어 반환되고 제너레이터 객체를 통해 실제로 반환 값에 접근할 때, 즉 반환 값이 실제로 필요한 순간에 해당 값이 메모리에 올라감
    → 지연 평가 + 순차적 접근
- 함수 실행이 중단될 때 함수의 상태가 저장되고 함수 실행이 재개될 때 앞의 상태로부터 실행이 시작됨
    - 제너레이터 객체 구조체가 마지막으로 실행한 `yield` 문의 프레임 객체를 유지
- 제너레이터에는 파이썬의 컨테이너 타입(리스트, 튜플 등)과 같이 이터레이터 프로토콜이 구현되어 있음
    - `__next__()`가 실행되면 실제로 함수가 실행되고 `yield` 키워드를 만나면 실행 중단

### 2.1 제너레이터의 구조

- 제너레이터 객체는 템플릿 매크로 `_PyGenObjec_HEAD(prefix)`에 의해 생성됨
    - 아래 접두사를 가진 타입들에서 이 매크로가 사용됨
        - 제너레이터 객체 : `PyGenObject(gi_)`
        - 코루틴 객체 : `PyCoroObject(cr_)`
        - 비동기 제너레이터 객체 : `PyAsyncGenObject(ag_)`
- `Include/genobject.h` > `_PyGenObject_HEAD(prefix)`
    
    ```c
    /* _PyGenObject_HEAD defines the initial segment of generator
       and coroutine objects. */
    #define _PyGenObject_HEAD(prefix)                                           
        PyObject_HEAD                                                           
        /* Note: gi_frame can be NULL if the generator is "finished" */         
        PyFrameObject *prefix##_frame;                                          
        /* True if generator is being executed. */                              
        char prefix##_running;                                                  
        /* The code object backing the generator */                             
        PyObject *prefix##_code;                                                
        /* List of weak reference. */                                           
        PyObject *prefix##_weakreflist;                                         
        /* Name of the generator. */                                            
        PyObject *prefix##_name;                                                
        /* Qualified name of the generator. */                                  
        PyObject *prefix##_qualname;                                            
        _PyErr_StackItem prefix##_exc_state;
    ```
    
    | 필드명 | 용도 |
    | --- | --- |
    | [x]_code | 제너레이터를 제공하는 컴파일된 함수 |
    | [x]_exc_state | 제너레이터 호출에서 예외가 발생했을 때 예외 데이터 |
    | [x]_frame | 제너레이터의 현재 프레임 객체 |
    | [x]_name | 제너레이터의 이름 |
    | [x]_qualnmae | 제너레이터의 정규화된 이름 |
    | [x]_running | 제너레이터가 실행중인지 여부 (0/1) |
    | [x]_weakreflist | 제너레이터 함수 안의 객체들에 대한 약한 참조 리스트 |
- `Include/genobject.h` > `PyGenObject`
    
    ```c
    typedef struct {
        /* The gi_ prefix is intended to remind of generator-iterator. */
        _PyGenObject_HEAD(gi)
    } PyGenObject;
    ```
    
- `Include/genobject.h` > `PyCoroObject`
    
    ```c
    typedef struct {
        _PyGenObject_HEAD(cr)
        PyObject *cr_origin;
    } PyCoroObject;
    ```
    
    | 필드명 | 용도 |
    | --- | --- |
    | cr_origin | 코루틴을 호출한 프레임과 함수를 담는 튜플 |
- `Include/genobject.h` > `PyAsyncGenObject`
    
    ```c
    typedef struct {
        _PyGenObject_HEAD(ag)
        PyObject *ag_finalizer;
    
        /* Flag is set to 1 when hooks set up by sys.set_asyncgen_hooks
           were called on the generator, to avoid calling them more
           than once. */
        int ag_hooks_inited;
    
        /* Flag is set to 1 when aclose() is called for the first time, or
           when a StopAsyncIteration exception is raised. */
        int ag_closed;
    
        int ag_running_async;
    } PyAsyncGenObject;
    ```
    
    | 필드명 | 용도 |
    | --- | --- |
    | ag_closed | 제너레이터가 종료됐음을 표시하는 플래그 |
    | ag_finalizer | 파이널라이저 메서드로의 연결 |
    | ag_hooks_initied | 훅이 초기화됐음을 표시하는 플래그 |
    | ag_running_async | 제너레이터가 실행 중임을 표시하는 플래그 |
- 연관된 소스 파일 목록
    - `Include/genobject.h`
    - `Objects/genobject.c`

### 2.2 제너레이터 생성하기

- `yield` 문이 포함된 함수는 컴파일되면 컴파일된 코드 객체에 추가 플래그 `CO_GENERATOR`가 설정됨
    
    ```python
    import dis 
    
    def letters():
        i = 97
        end = 97 + 26
        while i < end:
            yield chr(i)
            i += 1
    
    code = letters.__code__
    flags = code.co_flags
    
    print(flags)
    print(dis.COMPILER_FLAG_NAMES[32])
    print(flags & 32 > 0)
    
    """
    99
    GENERATOR
    True
    """
    ```
    
- 제너레이터, 코루틴, 비동기 제너레이터는 컴파일된 코드 객체를 프레임 객체로 변환할 때 특별하게 처리됨
    - `_PyEval_EvalCode()`는 코드 객체에서 위 플래그를 확인함
    - 플래그가 설정되어 있다면 평가 함수는 코드 객체를 바로 평가하는 대신 프레임을 만든 후 각각 아래 함수를 사용하여 변환함
        - 코드
            
            ```c
            /* Handle generator/coroutine/asynchronous generator */
            if (co->co_flags & (CO_GENERATOR | CO_COROUTINE | CO_ASYNC_GENERATOR)) {
                PyObject *gen;
                int is_coro = co->co_flags & CO_COROUTINE;
            
                /* Don't need to keep the reference to f_back, it will be set
                 * when the generator is resumed. */
                Py_CLEAR(f->f_back);
            
                /* Create a new generator that owns the ready to run frame
                 * and return that as the value. */
                if (is_coro) {
                    gen = PyCoro_New(f, name, qualname);
                } else if (co->co_flags & CO_ASYNC_GENERATOR) {
                    gen = PyAsyncGen_New(f, name, qualname);
                } else {
                    gen = PyGen_NewWithQualName(f, name, qualname);
                }
                if (gen == NULL) {
                    return NULL;
                }
            
                _PyObject_GC_TRACK(f);
            
                return gen;
            }
            ```
            
        - `PyGen_NewWithQualName()` → 제너레이터로 변환
        - `PyCoro_New()` → 코루틴으로 변환
        - `PyAsyncGen_New()` → 비동기 제너레이터로 변환
- `PyGen_NewWithQualName()`이 프레임을 통해 제너레이터 객체 필드를 채움
    - `gi_code` 프로퍼티에 컴파일된 코드 객체 설정
    - 제너레이터가 실행 중이 아님을 표시 (`gi_running = 0`)
    - 예외와 약한 참조 리스트를 NULL로 설정
- 역어셈블로 `gi_code`가 컴파일된 코드 객체임을 확인
    
    ```python
    import dis 
    
    def letters():
        i = 97
        end = 97 + 26
        while i < end:
            yield chr(i)
            i += 1
    
    generator = letters()
    dis.disco(generator.gi_code)
    
    """
      5           0 LOAD_CONST               1 (97)
                  2 STORE_FAST               0 (i)
    
      6           4 LOAD_CONST               2 (123)
      ...
    """
    ```
    

### 2.3 제너레이터 실행하기

- 제너레이터 객체의 `__next__()` 호출
- `gen_iternext()`가 제너레이터 인스턴스와 함께 호출됨
- `Objects/genobject.c`의 `gen_send_ex()` 호출
    - `gen_send_ex()` : 제너레이터 객체를 다음 `yield` 값으로 바꾸는 함수
        - 코드 객체로부터 프레임을 구성하는 로직과 상당히 비슷함
        - 제너레이터, 코루틴, 비동기 제너레이터 모두 해당 함수 사용
- `gen_send_ex()` 실행 순서
    - 전체 코드
        
        ```c
        gen_send_ex(PyGenObject *gen, PyObject *arg, int exc, int closing)
        {
            PyThreadState *tstate = _PyThreadState_GET();
            PyFrameObject *f = gen->gi_frame;
            PyObject *result;
        
            if (gen->gi_running) {
                const char *msg = "generator already executing";
                if (PyCoro_CheckExact(gen)) {
                    msg = "coroutine already executing";
                }
                else if (PyAsyncGen_CheckExact(gen)) {
                    msg = "async generator already executing";
                }
                PyErr_SetString(PyExc_ValueError, msg);
                return NULL;
            }
            if (f == NULL || f->f_stacktop == NULL) {
                if (PyCoro_CheckExact(gen) && !closing) {
                    /* `gen` is an exhausted coroutine: raise an error,
                       except when called from gen_close(), which should
                       always be a silent method. */
                    PyErr_SetString(
                        PyExc_RuntimeError,
                        "cannot reuse already awaited coroutine");
                }
                else if (arg && !exc) {
                    /* `gen` is an exhausted generator:
                       only set exception if called from send(). */
                    if (PyAsyncGen_CheckExact(gen)) {
                        PyErr_SetNone(PyExc_StopAsyncIteration);
                    }
                    else {
                        PyErr_SetNone(PyExc_StopIteration);
                    }
                }
                return NULL;
            }
        
            if (f->f_lasti == -1) {
                if (arg && arg != Py_None) {
                    const char *msg = "can't send non-None value to a "
                                      "just-started generator";
                    if (PyCoro_CheckExact(gen)) {
                        msg = NON_INIT_CORO_MSG;
                    }
                    else if (PyAsyncGen_CheckExact(gen)) {
                        msg = "can't send non-None value to a "
                              "just-started async generator";
                    }
                    PyErr_SetString(PyExc_TypeError, msg);
                    return NULL;
                }
            } else {
                /* Push arg onto the frame's value stack */
                result = arg ? arg : Py_None;
                Py_INCREF(result);
                *(f->f_stacktop++) = result;
            }
        
            /* Generators always return to their most recent caller, not
             * necessarily their creator. */
            Py_XINCREF(tstate->frame);
            assert(f->f_back == NULL);
            f->f_back = tstate->frame;
        
            gen->gi_running = 1;
            gen->gi_exc_state.previous_item = tstate->exc_info;
            tstate->exc_info = &gen->gi_exc_state;
        
            if (exc) {
                assert(_PyErr_Occurred(tstate));
                _PyErr_ChainStackItem(NULL);
            }
        
            result = _PyEval_EvalFrame(tstate, f, exc);
            tstate->exc_info = gen->gi_exc_state.previous_item;
            gen->gi_exc_state.previous_item = NULL;
            gen->gi_running = 0;
        
            /* Don't keep the reference to f_back any longer than necessary.  It
             * may keep a chain of frames alive or it could create a reference
             * cycle. */
            assert(f->f_back == tstate->frame);
            Py_CLEAR(f->f_back);
        
            /* If the generator just returned (as opposed to yielding), signal
             * that the generator is exhausted. */
            if (result && f->f_stacktop == NULL) {
                if (result == Py_None) {
                    /* Delay exception instantiation if we can */
                    if (PyAsyncGen_CheckExact(gen)) {
                        PyErr_SetNone(PyExc_StopAsyncIteration);
                    }
                    else {
                        PyErr_SetNone(PyExc_StopIteration);
                    }
                }
                else {
                    /* Async generators cannot return anything but None */
                    assert(!PyAsyncGen_CheckExact(gen));
                    _PyGen_SetStopIterationValue(result);
                }
                Py_CLEAR(result);
            }
            else if (!result && PyErr_ExceptionMatches(PyExc_StopIteration)) {
                const char *msg = "generator raised StopIteration";
                if (PyCoro_CheckExact(gen)) {
                    msg = "coroutine raised StopIteration";
                }
                else if (PyAsyncGen_CheckExact(gen)) {
                    msg = "async generator raised StopIteration";
                }
                _PyErr_FormatFromCause(PyExc_RuntimeError, "%s", msg);
        
            }
            else if (!result && PyAsyncGen_CheckExact(gen) &&
                     PyErr_ExceptionMatches(PyExc_StopAsyncIteration))
            {
                /* code in `gen` raised a StopAsyncIteration error:
                   raise a RuntimeError.
                */
                const char *msg = "async generator raised StopAsyncIteration";
                _PyErr_FormatFromCause(PyExc_RuntimeError, "%s", msg);
            }
        
            if (!result || f->f_stacktop == NULL) {
                /* generator can't be rerun, so release the frame */
                /* first clean reference cycle through stored exception traceback */
                _PyErr_ClearExcState(&gen->gi_exc_state);
                gen->gi_frame->f_gen = NULL;
                gen->gi_frame = NULL;
                Py_DECREF(f);
            }
        
            return result;
        }
        ```
        
    1. 현재 스레드 상태를 가져옴
    2. 제너레이터 객체로부터 프레임 객체를 가져옴
        
        ```c
        PyThreadState *tstate = _PyThreadState_GET();
        PyFrameObject *f = gen->gi_frame;
        ```
        
    3. 제너레이터가 실행 중이면 `ValueError`를 발생시킴
        
        ```c
        if (gen->gi_running) {
            const char *msg = "generator already executing";
            if (PyCoro_CheckExact(gen)) {
                msg = "coroutine already executing";
            }
            else if (PyAsyncGen_CheckExact(gen)) {
                msg = "async generator already executing";
            }
            PyErr_SetString(PyExc_ValueError, msg);
            return NULL;
        }
        ```
        
    4. 제너레이터 안의 프레임이 스택의 최상위에 위치해 있을 경우 처리
        
        ```c
        if (f == NULL || f->f_stacktop == NULL) {
            if (PyCoro_CheckExact(gen) && !closing) {
                /* `gen` is an exhausted coroutine: raise an error,
                   except when called from gen_close(), which should
                   always be a silent method. */
                PyErr_SetString(
                    PyExc_RuntimeError,
                    "cannot reuse already awaited coroutine");
            }
            else if (arg && !exc) {
                /* `gen` is an exhausted generator:
                   only set exception if called from send(). */
                if (PyAsyncGen_CheckExact(gen)) {
                    PyErr_SetNone(PyExc_StopAsyncIteration);
                }
                else {
                    PyErr_SetNone(PyExc_StopIteration);
                }
            }
            return NULL;
        }
        ```
        
    5. 프레임이 막 실행되기 시작해서 마지막 명령이 아직 -1이고 프레임이 코루틴이나 비동기 제너레이터인 경우 None 이외의 값을 인자로 넘기면 예외 발생
    6. 인자를 프레임의 값 스택에 추가
        
        ```c
        if (f->f_lasti == -1) {
            if (arg && arg != Py_None) {
                const char *msg = "can't send non-None value to a "
                                  "just-started generator";
                if (PyCoro_CheckExact(gen)) {
                    msg = NON_INIT_CORO_MSG;
                }
                else if (PyAsyncGen_CheckExact(gen)) {
                    msg = "can't send non-None value to a "
                          "just-started async generator";
                }
                PyErr_SetString(PyExc_TypeError, msg);
                return NULL;
            }
        } else {
            /* Push arg onto the frame's value stack */
            result = arg ? arg : Py_None;
            Py_INCREF(result);
            *(f->f_stacktop++) = result;
        }
        ```
        
    7. 프레임의 `f_back` 필드는 반환값을 전송할 호출자이기 때문에 이 필드에는 스레드의 현재 프레임이 설정됨 → 제너레이터를 생성한 곳이 아닌 제너레이터를 호출한 곳에 값이 반환됨
        
        ```c
        /* Generators always return to their most recent caller, not
         * necessarily their creator. */
        Py_XINCREF(tstate->frame);
        assert(f->f_back == NULL);
        f->f_back = tstate->frame;
        ```
        
    8. 제너레이터가 실행 중임을 표시 
    9. 제너레이터의 마지막 예외가 스레드 상태의 마지막 예외로 복사됨
    10. 스레드 상태의 예외 정보가 제너레이터의 예외 정보를 가리키도록 설정됨 → 호출자가 제너레이터 실행부 주변에 중단점을 추가할 때 스택트레이스가 제너레이터를 통과해 문제가 되는 코드가 명확해짐
        
        ```c
        gen->gi_running = 1;
        gen->gi_exc_state.previous_item = tstate->exc_info;
        tstate->exc_info = &gen->gi_exc_state;
        ```
        
    11. `Python/ceval.c`의 평가 루프에서 제너레이터 안의 프레임을 실행하고 값을 반환
    12. 스레드 상태의 마지막 예외 정보가 프레임 호출 전의 값으로 복구됨
    13. 제너레이터가 실행 중이 아니라고 표시됨
        
        ```c
        result = _PyEval_EvalFrame(tstate, f, exc);
        tstate->exc_info = gen->gi_exc_state.previous_item;
        gen->gi_exc_state.previous_item = NULL;
        gen->gi_running = 0;
        ```
        
    14. 반환값에 따라 예외를 발생시킴
    15. 결과가 `__next__()` 호출자에 반환됨
        
        ```c
        /* If the generator just returned (as opposed to yielding), signal
         * that the generator is exhausted. */
        if (result && f->f_stacktop == NULL) {
            if (result == Py_None) {
                /* Delay exception instantiation if we can */
                if (PyAsyncGen_CheckExact(gen)) {
                    PyErr_SetNone(PyExc_StopAsyncIteration);
                }
                else {
                    PyErr_SetNone(PyExc_StopIteration);
                }
            }
            else {
                /* Async generators cannot return anything but None */
                assert(!PyAsyncGen_CheckExact(gen));
                _PyGen_SetStopIterationValue(result);
            }
            Py_CLEAR(result);
        }
        else if (!result && PyErr_ExceptionMatches(PyExc_StopIteration)) {
            const char *msg = "generator raised StopIteration";
            if (PyCoro_CheckExact(gen)) {
                msg = "coroutine raised StopIteration";
            }
            else if (PyAsyncGen_CheckExact(gen)) {
                msg = "async generator raised StopIteration";
            }
            _PyErr_FormatFromCause(PyExc_RuntimeError, "%s", msg);
        
        }
        else if (!result && PyAsyncGen_CheckExact(gen) &&
                 PyErr_ExceptionMatches(PyExc_StopAsyncIteration))
        {
            /* code in `gen` raised a StopAsyncIteration error:
               raise a RuntimeError.
            */
            const char *msg = "async generator raised StopAsyncIteration";
            _PyErr_FormatFromCause(PyExc_RuntimeError, "%s", msg);
        }
        
        if (!result || f->f_stacktop == NULL) {
            /* generator can't be rerun, so release the frame */
            /* first clean reference cycle through stored exception traceback */
            _PyErr_ClearExcState(&gen->gi_exc_state);
            gen->gi_frame->f_gen = NULL;
            gen->gi_frame = NULL;
            Py_DECREF(f);
        }
        
        return result;
        ```
        

## 3. 코루틴

- 코루틴
    - 실행을 중단하고 재개할 수 있는 함수, 특정 시점에서 작업을 중단하고 다른 작업을 수행할 수 있음
    - 호출자와 호출된 함수 사이의 제어 흐름이 상호작용
    - 비동기 프로그래밍에서 사용

### 3.1 제너레이터 기반 코루틴

- 제너레이터는 함수 실행을 중지하고 재개할 수 있음 → 이러한 동작에 기반을 두고 제너레이터 기반 코루틴이 만들어짐
- 값을 생성하여 호출자에게 전달하기만 하는 제너레이터와 달리 코루틴은 호출자와 양방향 통신 가능 (`send()` 메서드 사용)
- 제너레이터의 한계는 직접적인 호출자에게만 값을 제공할 수 있다는 것 → `yield from`을 통해 극복
    - 제너레이터 함수를 유틸리티 함수로 리팩토링 가능
    - 다른 제너레이터로부터 값을 받아온 뒤 현재 제너레이터의 호출자에게 반환
    - 예시
        
        ```python
        def gen_letters():
            i = 97
            end = 97 + 26
            while i < end:
                yield chr(i)
                i += 1
        
        def letters(upper):
            if upper:
                yield from gen_letters(65, 26)
            else:
                yield from gen_letters(97, 26)
        
        for letter in letters(True):
            print(letter)
        
        for letter in letters(False):
            print(letter)
        ```
        
- `yield from`을 통해 다른 코루틴에 값을 전달할 수 있으므로 복잡한 비동기 코드 관리에 유용
- 데코레이터를 사용하여 구현 → 네이티브 코루틴이 선호되어 더이상 쓰지 않음

### 3.2 네이티브 코루틴

- 함수 앞에 `async` 키워드를 명시하여 코루틴을 반환함을 표시
- `asyncio.run()`을 통해 코루틴 객체 실행
    - 코드 (`Lib/asyncio/runners.py`)
        
        ```python
        def run(main, *, debug=None):
            """Execute the coroutine and return the result.
        
            This function runs the passed coroutine, taking care of
            managing the asyncio event loop and finalizing asynchronous
            generators.
        
            This function cannot be called when another asyncio event loop is
            running in the same thread.
        
            If debug is True, the event loop will be run in debug mode.
        
            This function always creates a new event loop and closes it at the end.
            It should be used as a main entry point for asyncio programs, and should
            ideally only be called once.
        
            Example:
        
                async def main():
                    await asyncio.sleep(1)
                    print('hello')
        
                asyncio.run(main())
            """
            if events._get_running_loop() is not None:
                raise RuntimeError(
                    "asyncio.run() cannot be called from a running event loop")
        
            if not coroutines.iscoroutine(main):
                raise ValueError("a coroutine was expected, got {!r}".format(main))
        
            loop = events.new_event_loop()
            try:
                events.set_event_loop(loop)
                if debug is not None:
                    loop.set_debug(debug)
                return loop.run_until_complete(main)
            finally:
                try:
                    _cancel_all_tasks(loop)
                    loop.run_until_complete(loop.shutdown_asyncgens())
                    loop.run_until_complete(loop.shutdown_default_executor())
                finally:
                    events.set_event_loop(None)
                    loop.close()
        ```
        
    - 실행 순서
        1. 새 이벤트 루프를 시작
        2. 코루틴 객체를 태스크로 감싸기
        3. 태스크가 완료될 때 실행할 콜백을 설정
        4. 태스크가 완료될 때까지 루프를 반복
        5. 결과 반환
- 예시
    
    ```python
    import asyncio
    
    async def sleepy_alarm(time):
        await asyncio.sleep(time)
        return "wake up!"
    
    alarm = asyncio.run(sleepy_alarm(5))
    print(alarm)
    ```
    
- 장점
    - 여러 코루틴 동시 실행 가능
    - 코루틴 객체를 다른 함수의 인자로 사용 가능 → 코루틴 객체를 서로 연결하여 연쇄적으로 처리하거나 순차적으로 생성 가능
- 연관된 소스 파일 목록
    - `Lib/asyncio`

### 3.3 이벤트 루프

- 비동기 코드를 연결하는 접착제 역할
- 순수한 파이썬으로 작성된 이벤트 루프는 태스크를 보관하는 객체
    - `asyncio.Task` 타입으로 표현되는 일련의 태스크로 이루어짐
    - 태스크를 루프에 예약 → 루프가 한 번 실행되면 모든 태스크가 완료될 때까지 태스크 순회
    - 태스크에 콜백을 등록하여 작업이 완료되거나 실패하면 이벤트 루프가 등록된 콜백을 실행시킴
- `yield` 키워드가 같은 프레임에서 여러 값을 반환할 수 있는 것처럼 `await` 키워드도 여러 상태 반환 가능
- 예시
    
    ```python
    import asyncio
    
    async def sleepy_alarm(person, time):
        await asyncio.sleep(time)
        print(f"{person} -- wake up!")
    
    async def wake_up_gang():
        tasks = [
            asyncio.create_task(sleepy_alarm("Bob", 3), name="wake up Bob"),
            asyncio.create_task(sleepy_alarm("Andy", 4), name="wake up Andy"),
            asyncio.create_task(sleepy_alarm("Sam", 2), name="wake up Sam")
        ]
        await asyncio.gather(*tasks)
    
    asyncio.run(wake_up_gang())
    
    """
    Sam -- wake up!
    Bob -- wake up!
    Andy -- wake up!
    """
    ```
    

## 4. 비동기 제너레이터

- 제너레이터와 네이티브 코루틴의 개념을 하나로 합친 것
- 함수가 `async` 키워드를 사용하여 선언되었고 `yield` 문을 포함한다면 호출 시 비동기 제너레이터로 변환
- 제너레이터처럼 이터레이터 프로토콜을 사용하여 실행됨
    - 제너레이터 : `for` / `__next__()`
    - 비동기 제너레이터 : `async for` / `__anext__()`

## 5. 서브인터프리터

- 멀티프로세싱을 활용한 병렬 실행
    - 파이프와 큐를 사용하여 공유 메모리 대비 느린 프로세스 간 통신 방식 사용
    - 새 프로세스 시작 시 오버헤드
- 스레드와 비동기를 활용한 동시 실행
    - 오버헤드가 적지만 스레드 안전성을 제공하는 GIL로 인해 진정한 병렬 실행이 아님
- 서브인터프리터 : 여러 개의 독립적인 인터프리터 인스턴스를 생성하여 사용
    - 진정한 병렬 실행인 동시에 멀티프로세싱에 비해 오버헤드가 적음
- `Py_NewInterpreter()`와 같은 저수준 인터프리터 생성 C API 제공
- 모든 파이썬 객체의 포인터가 보관되는 메모리 할당 아레나를 인터프리터 상태에서 관리하므로 각 인터프리터는 다른 인터프리터의 변수에 접근 불가
    - 인터프리터 간 객체 공유를 위해서는 직렬화하거나 `ctypes`를 사용하고 IPC 형태로 공유해야 함
- 연관된 소스 파일 목록
    - `Lib/_xxsubinterpreters.c`
    - `Python/pylifecycle.c`

## 6. Port Scanner: `asyncio`, Async Generator, Subinterpreter

### 6.1 멀티 스레딩

```python
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue

timeout = 1.0

def check_port(host: str, port: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        if result == 0:
            return port
    return None

def main():
    start = time.time()
    host = "localhost"  # Replace with a host you own
    open_ports = []
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(check_port, host, port) for port in range(30000, 65536)]
        
        for future in as_completed(futures):
            port = future.result()
            if port is not None:
                open_ports.append(port)
    
    for port in open_ports:
        print(f"Port {port} is open")
    print(f"Completed scan in {time.time() - start:.2f} seconds")

if __name__ == '__main__':
    main()
```

- 3 ~ 3.5초

### 6.2 `asyncio`

```python
import time
import asyncio

timeout = 1.0

async def check_port(host: str, port: int, results: list):
    try:
        future = asyncio.open_connection(host=host, port=port)
        r, w = await asyncio.wait_for(future, timeout=timeout)
        results.append(port)
        w.close()
    except OSError:  # do not throw an exception when port is not open
        pass
    except asyncio.TimeoutError:
        pass # closed

async def scan(start, end, host):
    tasks = []
    results = []
    for port in range(start, end):
        tasks.append(check_port(host, port, results))
    await asyncio.gather(*tasks)
    return results

if __name__ == '__main__':
    start = time.time()
    host = "localhost"
    results = asyncio.run(scan(30000, 65536, host))
    for result in results:
        print("Port {0} is open".format(result))
    print("Completed scan in {0} seconds".format(time.time() - start))
```

- 4 ~4.8초
- 멀티 스레딩 코드와 다른 결과 출력

### 6.3 비동기 제너레이터

```python
import time
import asyncio

timeout = 1.0

async def check_ports(host: str, start: int, end: int, max=10):
    found = 0
    for port in range(start, end):
        try:
            future = asyncio.open_connection(host=host, port=port)
            r, w = await asyncio.wait_for(future, timeout=timeout)
            yield port
            found += 1
            w.close()
            if found >= max:
                return
        except OSError:
            pass
        except ConnectionRefusedError:
            pass
        except asyncio.TimeoutError:
            pass # closed

async def scan(start, end, host):
    results = []
    async for port in check_ports(host, start, end, max=1):
        results.append(port)
    return results

if __name__ == '__main__':
    start = time.time()
    host = "localhost"
    scan_range = 30000, 65536
    results = asyncio.run(scan(*scan_range, host))
    for result in results:
        print("Port {0} is open".format(result))
    print("Completed scan in {0} seconds".format(time.time() - start))
```

- 1.5 ~ 1.9초
- 멀티 스레딩 코드와 다른 결과 출력

### 6.4 서브 인터프리터

```python
import time
import _xxsubinterpreters as subinterpreters
from threading import Thread
import textwrap as tw
from queue import Queue

timeout = 1  # in seconds..

def run(host: str, port: int, results: Queue):
    # Create a communication channel
    channel_id = subinterpreters.channel_create()
    interpid = subinterpreters.create()
    subinterpreters.run_string(
        interpid,
        tw.dedent(
    """
    import socket; import _xxsubinterpreters as subinterpreters
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((host, port))
    subinterpreters.channel_send(channel_id, result)
    sock.close()
    """),
        shared=dict(
            channel_id=channel_id,
            host=host,
            port=port,
            timeout=timeout
        ))
    output = subinterpreters.channel_recv(channel_id)
    subinterpreters.channel_release(channel_id)
    if output == 0:
        results.put(port)

if __name__ == '__main__':
    start = time.time()
    host = "localhost"  # pick a friend
    threads = []
    results = Queue()
    for port in range(30000, 65536):
        t = Thread(target=run, args=(host, port, results))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    while not results.empty():
        print("Port {0} is open".format(results.get()))
    print("Completed scan in {0} seconds".format(time.time() - start))
```
