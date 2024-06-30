# 11. 객체와 타입

## 11.1 Python에서의 객체란?

(참고: https://docs.python.org/ko/3.9/reference/datamodel.html)

객체(Objects)는 데이터를 추상화한 것으로, Python 내에서 모든 데이터는 객체와 객체 간의 관계로 표현합니다.
(폰 노이만의 “프로그램 내장식 컴퓨터(stored program computer)” 모델을 따릅니다.)

> “프로그램 내장식 컴퓨터(stored program computer)” 모델
> <br>: 컴퓨터 내부에 프로그램과 데이터를 저장 → 컴퓨터가 필요한 내용을 순서에 따라 인출하고 해독 → 프로그램 자체와 데이터를 동일한 형태로 메모리에 저장할 수 있는 구조

모든 객체는 identity, type, value를 가집니다.
- identity
<br>: 메모리 상에서의 객체 주소로, `id()` 통해 확인 가능합니다.
- type
<br>: 각 타입별 소스 파일은 `Objects`에 저장되어 있으며, 소스 파일에 대한 헤더 파일은 `Include`에 포함되어 있습니다.
- value
<br>: 객체에 대한 값으로, 변경 가능 여부에 따라 가변(mutable) / 불변(immutable) 으로 분류됩니다.

내장된 대표 객체 목록은 다음과 같습니다.
- None
- Ellipsis (…)
- numbers.Number
    - numbers.Integral: int, bool
    - numbers.Real
    - numbers.Complex
- Sequences
    - 불변: string, tuple, byte
    - 가변: list, byte array
- Set types
    - set
    - frozen set
- Mappings
    - dictionary

## 11.2 객체 구조체 (기본 & 가변 객체 타입)

(참고: https://docs.python.org/3/c-api/structures.html)


### PyObject

모든 파이썬 객체의 기본 구조체로, 크기가 고정된 immutable 객체에 사용합니다.
<br>(ex: `int`, `float`)
    
```c
// Include/object.h

/* Nothing is actually declared to be a PyObject, 
    but every pointer to a Python object can be cast to a PyObject*.  
    This is inheritance built by hand.
    Similarly every pointer to a variable-size Python object can, 
    in addition, be cast to PyVarObject*.
    */
typedef struct _object {
    _PyObject_HEAD_EXTRA
    Py_ssize_t ob_refcnt;   // 인스턴스 레퍼런스 카운터
    [PyTypeObject](https://www.notion.so/Chapter-11-d7671cb0ccd049a780f58d2191efee53?pvs=21) *ob_type;  // 객체 타입
} PyObject;
```

`_PyObject_HEAD_EXTRA`는 모든 파이썬 객체를 doubly linked list로 만들어서 → 메모리 누수 또는 객체 생성/소멸 문제 디버깅 시 사용합니다.
<br>(디버깅 모드에서만 사용)
    
```c
/* Define pointers to support a doubly-linked list of all live heap objects. */
#define _PyObject_HEAD_EXTRA            \
    struct _object *_ob_next;           \
    struct _object *_ob_prev;
```
    
타입 정의 시에는 `PyObject_HEAD`를 사용합니다.
    
```c
/* PyObject_HEAD defines the initial segment of every PyObject. */
#define PyObject_HEAD          PyObject ob_base;
```
    
- ex) PyFloatObject
    ```c
    // Include/floatobject.h
    typedef struct {
        **PyObject_HEAD**
        double ob_fval;  // 실제 float 값 정의
    } PyFloatObject;
    ```

### PyVarObject

가변 크기 객체의 기본 구조체로, 길이가 런타임에 변할 수 있는 mutable 객체에 사용합니다.
<br>(ex: `list`, `str`, `tuple`)
    
```c
// Include/object.h
typedef struct {
    PyObject ob_base;   // 기반 타입
    Py_ssize_t ob_size; // 객체 크기
} PyVarObject;
```

타입 정의 시에는 `PyObject_VAR_HEAD`를 사용합니다.
    
```c
/* PyObject_VAR_HEAD defines the initial segment of all variable-size container objects.
    These end with a declaration of an array with 1 element, 
    but enough space is malloc'ed so that the array actually has room for ob_size elements.
    Note that ob_size is an element count, not necessarily a byte count. */
#define PyObject_VAR_HEAD      PyVarObject ob_base;
```
    
- ex) PyLongObject
    ```c
    // Include/longobject.h
    typedef struct _longobject PyLongObject; /* Revealed in longintrepr.h */

    // Include/longintrepr.h
    struct _longobject {
        **PyObject_VAR_HEAD**
        digit ob_digit[1];
    };
    ```
    

## 11.3 PyTypeObject: 객체 type 표현

(참고: https://docs.python.org/3.9/c-api/typeobj.html)

PyObject 정의에서 해당 객체가 어떤 type을 나타내는지 표현하기 위해 사용하며, 객체의 모든 행동(메소드, 속성 접근, 생성, 소멸 등)을 정의합니다.
    
```c
typedef struct _object {
    _PyObject_HEAD_EXTRA
    Py_ssize_t ob_refcnt;   // 인스턴스 레퍼런스 카운터
    **PyTypeObject *ob_type;**  // 객체 타입
} PyObject;
```

파이썬의 "모든 것이 객체"라는 철학의 핵심 하에, `PyTypeObject` 자체도 `PyObject` 형식으로 볼 수 있습니다.
    
```c
/* PyTypeObject structure is defined in cpython/object.h.
    In Py_LIMITED_API, PyTypeObject is an opaque structure. */
typedef struct _typeobject PyTypeObject;
```
    

### type slot (PyTypeObject 구조체 필드)

PyTypeObject 구조체 내 필드를 나타내며, 각 필드는 특정 기능을 구현하는 함수에 대한 포인터를 가리킵니다.
`type()`을 통해 PyTypeObject 인스턴스를 반환하며, `__init__`, `__repr__`  등 특수 메소드 등에 대응합니다.

```c
// Include/cpython/object.h
struct _typeobject {
    PyObject_VAR_HEAD
    const char *tp_name;   /* type명 ("<module>.<name>" 형태) */
    Py_ssize_t tp_basicsize, tp_itemsize; /* For allocation */

    /* Methods to implement standard operations */

    destructor tp_dealloc;
    Py_ssize_t tp_vectorcall_offset;
    getattrfunc tp_getattr;
    setattrfunc tp_setattr;
    PyAsyncMethods *tp_as_async; /* formerly known as tp_compare (Python 2)
                                    or tp_reserved (Python 3) */
    reprfunc tp_repr;

    /* Method suites for standard classes */

    PyNumberMethods *tp_as_number;
    PySequenceMethods *tp_as_sequence;
    PyMappingMethods *tp_as_mapping;

    /* More standard operations (here for binary compatibility) */

    hashfunc tp_hash;
    ternaryfunc tp_call;
    reprfunc tp_str;
    getattrofunc tp_getattro;
    setattrofunc tp_setattro;

    /* Functions to access object as input/output buffer */
    PyBufferProcs *tp_as_buffer;

    /* Flags to define presence of optional/expanded features */
    unsigned long tp_flags;

    const char *tp_doc; /* type 설명 문서 문자열 */

    /* Assigned meaning in release 2.0 */
    /* call function for all accessible objects */
    traverseproc tp_traverse;

    /* delete references to contained objects */
    inquiry tp_clear;

    /* Assigned meaning in release 2.1 */
    /* rich comparisons */
    richcmpfunc tp_richcompare;

    /* weak reference enabler */
    Py_ssize_t tp_weaklistoffset;

    /* Iterators */
    getiterfunc tp_iter;
    iternextfunc tp_iternext;

    /* Attribute descriptor and subclassing stuff */
    struct PyMethodDef *tp_methods;
    struct PyMemberDef *tp_members;
    struct PyGetSetDef *tp_getset;
    struct _typeobject *tp_base;
    PyObject *tp_dict;
    descrgetfunc tp_descr_get;
    descrsetfunc tp_descr_set;
    Py_ssize_t tp_dictoffset;
    initproc tp_init;
    allocfunc tp_alloc;
    newfunc tp_new;
    freefunc tp_free; /* Low-level free-memory routine */
    inquiry tp_is_gc; /* For PyObject_IS_GC */
    PyObject *tp_bases;
    PyObject *tp_mro; /* method resolution order */
    PyObject *tp_cache;
    PyObject *tp_subclasses;
    PyObject *tp_weaklist;
    destructor tp_del;

    /* Type attribute cache version tag. Added in version 2.6 */
    unsigned int tp_version_tag;

    destructor tp_finalize;
    vectorcallfunc tp_vectorcall;
};
```
    
#### type slot 목록
- 기본 정보
    - `const char *tp_name`: 타입의 이름 (예: `"collections.defaultdict"`)
    - `const char *tp_doc`: 타입의 문서 문자열 (`help(type)`으로 확인 가능)
- 객체 생명주기
    - `newfunc tp_new`: 객체 생성 (`__new__`)
    - `initproc tp_init`: 객체 초기화 (`__init__`)
    - `destructor tp_dealloc`: 메모리 해제 (객체가 소멸될 때 호출)
- 문자열 표현
    - `reprfunc tp_repr`: 개발자용 문자열 표현 (`__repr__`)
    - `reprfunc tp_str`: 사용자 친화적 문자열 표현 (`__str__`)
- 속성 및 메서드 접근
    - `getattrofunc tp_getattro`: 속성 접근 (`__getattribute__`)
    - `setattrofunc tp_setattro`: 속성 설정 (`__setattr__`)
    - `struct PyMethodDef *tp_methods`: method 정의 테이블
- 연산자 및 특수 method
    - `PyNumberMethods *tp_as_number`: 숫자 연산 (+, - 등)
    - `PySequenceMethods *tp_as_sequence`: 시퀀스 연산 (`len()`, 인덱싱 등)
    - `hashfunc tp_hash`: 해시 값 계산 (`__hash__`)
    - `ternaryfunc tp_call`: 객체를 함수처럼 호출 (`__call__`)
- 상속 및 타입 관계
    - `struct _typeobject *tp_base`: 기본 클래스
    - `PyObject *tp_bases`: 기본 클래스들의 튜플
    - `PyObject *tp_mro`: method 해결 순서 (Method Resolution Order)

#### type slot 종류
- `tp_`: 기본 type slot
- `nb_`: 숫자 연산 관련 method
    - nb_add: +
    - nb_subtract: -
    - nb_multiply: *
    - nb_true_divide: /
    - nb_power: **
- `sq_`: sequence 연산 관련 method
    - sq_length: len()
    - sq_concat: +로 sequence 연결
    - sq_repeat: *로 sequence 반복
    - sq_item: [] 통한 인덱싱
- `mp_`: mapping(dictionary) 연산 관련 method
    - mp_length: len()
    - mp_subscript: []로 key 접근
- `am_`: async 관련 method
    - am_await: __await__
    - am_aiter: __aiter__
    - am_anext: __anext__
- `bf_`: buffer protocol 관련 method (bytes, bytearray 등에서 사용)
    - bf_getbuffer: __buffer__
    - bf_releasebuffer: buffer 해제

## 11.4 타입별 내부 구조 살펴보기

### bool

- long을 상속해서 만들어집니다. (구조체가 따로 정의되어 있지 않고, PyLongObject를 사용하여 정의됩니다.)
- 불변 인스턴스 상수 Py_True / Py_False 로 표시합니다.
- type 정의 (PyBool_Type)
    
    ```c
    // Objects/boolobject.c
    PyTypeObject PyBool_Type = {
        PyVarObject_HEAD_INIT(&PyType_Type, 0)
        "bool",
        sizeof(struct _longobject),
        0,
        0,                                          /* tp_dealloc */
        0,                                          /* tp_vectorcall_offset */
        0,                                          /* tp_getattr */
        0,                                          /* tp_setattr */
        0,                                          /* tp_as_async */
        bool_repr,                                  /* tp_repr */
        &bool_as_number,                            /* tp_as_number */
        0,                                          /* tp_as_sequence */
        0,                                          /* tp_as_mapping */
        0,                                          /* tp_hash */
        0,                                          /* tp_call */
        0,                                          /* tp_str */
        0,                                          /* tp_getattro */
        0,                                          /* tp_setattro */
        0,                                          /* tp_as_buffer */
        Py_TPFLAGS_DEFAULT,                         /* tp_flags */
        bool_doc,                                   /* tp_doc */
        0,                                          /* tp_traverse */
        0,                                          /* tp_clear */
        0,                                          /* tp_richcompare */
        0,                                          /* tp_weaklistoffset */
        0,                                          /* tp_iter */
        0,                                          /* tp_iternext */
        0,                                          /* tp_methods */
        0,                                          /* tp_members */
        0,                                          /* tp_getset */
        **&PyLong_Type,                               /* tp_base */**
        0,                                          /* tp_dict */
        0,                                          /* tp_descr_get */
        0,                                          /* tp_descr_set */
        0,                                          /* tp_dictoffset */
        0,                                          /* tp_init */
        0,                                          /* tp_alloc */
        **bool_new,                                   /* tp_new */**
    };
    ```
    
    - bool_new (tp_new)
        
        ```c
        // Objects/boolobject.c
        static PyObject *
        bool_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
        {
            PyObject *x = Py_False;
            long ok;
        
            if (!_PyArg_NoKeywords("bool", kwds))
                return NULL;
            if (!PyArg_UnpackTuple(args, "bool", 0, 1, &x))
                return NULL;
            **ok = PyObject_IsTrue(x);**
            if (ok < 0)
                return NULL;
            **return PyBool_FromLong(ok);**
        }
        ```
        
    - PyObject_IsTrue
        
        ```c
        // Objects/object.c
        int
        PyObject_IsTrue(PyObject *v)
        {
            Py_ssize_t res;
            if (v == Py_True)
                return 1;
            if (v == Py_False)
                return 0;
            if (v == Py_None)
                return 0;
                
            else if (Py_TYPE(v)->tp_as_number != NULL &&
                        Py_TYPE(v)->tp_as_number->nb_bool != NULL)
                // 숫자 타입이고 nb_bool이 정의되어 있으면 -> nb_bool 결과 저장
                res = (*Py_TYPE(v)->tp_as_number->nb_bool)(v);
                
            else if (Py_TYPE(v)->tp_as_mapping != NULL &&
                        Py_TYPE(v)->tp_as_mapping->mp_length != NULL)
                // 매핑 타입이고 mp_length가 정의되어 있으면 -> mp_length 결과 저장
                res = (*Py_TYPE(v)->tp_as_mapping->mp_length)(v);
                
            else if (Py_TYPE(v)->tp_as_sequence != NULL &&
                        Py_TYPE(v)->tp_as_sequence->sq_length != NULL)
                // 시퀀스 타입이고 sq_length가 정의되어 있으면 -> sq_length 결과 저장
                res = (*Py_TYPE(v)->tp_as_sequence->sq_length)(v);
        
            else
                // 위에 다 해당하지 않으면 1 반환
                return 1;
        
            /* if it is negative, it should be either -1 or -2 */
            // 0보다 크면 1을 반환 / 0또는 음수이면 int로 변환해서 반환
            return (res > 0) ? 1 : Py_SAFE_DOWNCAST(res, Py_ssize_t, int);
        }
        ```
        
    - PyBool_FromLong
        
        ```c
        // Objects/boolobject.c
        
        /* Function to return a bool from a C long 
        (숫자로부터 bool 인스턴스를 생성하는 헬퍼 함수) */
        PyObject *PyBool_FromLong(long ok)
        {
                PyObject *result;
                
                if (ok)
                        result = Py_True;
                else
                        result = Py_False;
                Py_INCREF(result);
                return result;
        }
        ```
        
    - Py_True / Py_False
        
        ```c
        // Include/boolobject.h
        /* Don't use these directly */
        PyAPI_DATA(struct _longobject) _Py_FalseStruct, _Py_TrueStruct;  // PyAPI_DATA: Python 인터프리터의 내부 데이터에 대한 접근을 정의
        
        /* Use these macros */
        #define Py_False ((PyObject *) &_Py_FalseStruct)
        #define Py_True ((PyObject *) &_Py_TrueStruct)
        ```
        
        ```c
        // Objects/boolobject.c
        struct _longobject _Py_FalseStruct = {
            PyVarObject_HEAD_INIT(&PyBool_Type, 0)
            { 0 }
        };
        /*
        struct _longobject _Py_FalseStruct = {
            {
                1,             // 참조 횟수
                &PyBool_Type,  // 타입
                0              // 크기
            },
            { 0 }               // 정수 값 (False)
        };
        */
        
        struct _longobject _Py_TrueStruct = {
            PyVarObject_HEAD_INIT(&PyBool_Type, 1)
            { 1 }
        };
        /*
        struct _longobject _Py_TrueStruct = {
            {
                1,             // 참조 횟수
                &PyBool_Type,  // 타입
                1              // 크기
            },
            { 1 }               // 정수 값 (True)
        };
        */
        ```
            

### long

- python2 → python3 로 전환되면서 int 타입 지원을 버리고 long 정수 타입을 사용하고 있습니다.
    
    ```c
    // Objects/object.c
    INIT_TYPE(&PyLong_Type, "int");
    ```
    
- 가변 길이 숫자 저장이 가능합니다. (정수 최대 길이는 컴파일된 바이너리에 설정되어 있습니다.)
- 구조체
    ```c
    // Include/longobject.h
    typedef struct _longobject PyLongObject; /* Revealed in longintrepr.h */
    
    // Include/longintrepr.h
    struct _longobject {
        **PyObject_VAR_HEAD**
        digit ob_digit[1];
    };
    ```
    
    - ex) 1 → ob_digit: [1]
          24601 → ob_digit: [2,4,6,0,1]
- type 정의 (PyLong_Type)
    
    ```c
    // Objects/longobject.c
    PyTypeObject PyLong_Type = {
        PyVarObject_HEAD_INIT(&PyType_Type, 0)
        "int",                                      /* tp_name */
        offsetof(PyLongObject, ob_digit),           /* tp_basicsize */
        sizeof(digit),                              /* tp_itemsize */
        0,                                          /* tp_dealloc */
        0,                                          /* tp_vectorcall_offset */
        0,                                          /* tp_getattr */
        0,                                          /* tp_setattr */
        0,                                          /* tp_as_async */
        long_to_decimal_string,                     /* tp_repr */
        &long_as_number,                            /* tp_as_number */
        0,                                          /* tp_as_sequence */
        0,                                          /* tp_as_mapping */
        (hashfunc)long_hash,                        /* tp_hash */
        0,                                          /* tp_call */
        0,                                          /* tp_str */
        PyObject_GenericGetAttr,                    /* tp_getattro */
        0,                                          /* tp_setattro */
        0,                                          /* tp_as_buffer */
        Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE |
            Py_TPFLAGS_LONG_SUBCLASS,               /* tp_flags */
        long_doc,                                   /* tp_doc */
        0,                                          /* tp_traverse */
        0,                                          /* tp_clear */
        long_richcompare,                           /* tp_richcompare */
        0,                                          /* tp_weaklistoffset */
        0,                                          /* tp_iter */
        0,                                          /* tp_iternext */
        long_methods,                               /* tp_methods */
        0,                                          /* tp_members */
        long_getset,                                /* tp_getset */
        0,                                          /* tp_base */
        0,                                          /* tp_dict */
        0,                                          /* tp_descr_get */
        0,                                          /* tp_descr_set */
        0,                                          /* tp_dictoffset */
        0,                                          /* tp_init */
        0,                                          /* tp_alloc */
        **long_new,                                   /* tp_new */**
        PyObject_Del,                               /* tp_free */
    };
    ```
    
    - long_new
        
        ```c
        static PyObject *
        long_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
        {
            PyObject *return_value = NULL;
            static const char * const _keywords[] = {"", "base", NULL};  // 허용되는 키워드 인자
            static _PyArg_Parser _parser = {NULL, _keywords, "int", 0};  // 인자 파서
            PyObject *argsbuf[2];  // 임시 버퍼
            PyObject * const *fastargs;  // 빠르게 접근할 수 있는 인자 배열
            Py_ssize_t nargs = PyTuple_GET_SIZE(args);  // 위치 인자 개수
            Py_ssize_t noptargs = nargs + (kwargs ? PyDict_GET_SIZE(kwargs) : 0) - 0;  // 위치 인자와 키워드 인자의 총 개수
            PyObject *x = NULL;       // 실제 값
            PyObject *obase = NULL;   // base 키워드 인자
        
        		// args 인자 파싱 진행
            fastargs = _PyArg_UnpackKeywords(_PyTuple_CAST(args)->ob_item, nargs, kwargs, NULL, &_parser, 0, 2, 0, argsbuf);
            if (!fastargs) {
                goto exit;
            }
            if (nargs < 1) {
                goto skip_optional_posonly;
            }
            noptargs--;
            x = fastargs[0];
        skip_optional_posonly:
            if (!noptargs) {
                goto skip_optional_pos;
            }
            obase = fastargs[1];
        skip_optional_pos:
            **return_value = long_new_impl(type, x, obase);**
        
        exit:
            return return_value;
        }
        ```
        
    - long_new_impl
        
        ```c
        static PyObject *
        long_new_impl(PyTypeObject *type, PyObject *x, PyObject *obase)
        /*[clinic end generated code: output=e47cfe777ab0f24c input=81c98f418af9eb6f]*/
        {
            Py_ssize_t base;
        
            if (type != &PyLong_Type)
                return long_subtype_new(type, x, obase); /* Wimp out */
            if (x == NULL) {
                if (obase != NULL) {
                    PyErr_SetString(PyExc_TypeError,
                                    "int() missing string argument");
                    return NULL;
                }
                return PyLong_FromLong(0L);
        ****    }
            /* default base and limit, forward to standard implementation */
            if (obase == NULL)
                return PyNumber_Long(x);
        
            base = PyNumber_AsSsize_t(obase, NULL);
            if (base == -1 && PyErr_Occurred())
                return NULL;
            if ((base != 0 && base < 2) || base > 36) {
                PyErr_SetString(PyExc_ValueError,
                                "int() base must be >= 2 and <= 36, or 0");
                return NULL;
            }
        
            if (PyUnicode_Check(x))
                return PyLong_FromUnicodeObject(x, (int)base);
            else if (PyByteArray_Check(x) || PyBytes_Check(x)) {
                const char *string;
                if (PyByteArray_Check(x))
                    string = PyByteArray_AS_STRING(x);
                else
                    string = PyBytes_AS_STRING(x);
                return _PyLong_FromBytes(string, Py_SIZE(x), (int)base);
            }
            else {
                PyErr_SetString(PyExc_TypeError,
                                "int() can't convert non-string with explicit base");
                return NULL;
            }
        }
        ```
        
    - PyLong_FromLong
        
        ```c
        PyObject *
        PyLong_FromLong(long ival)
        {
            PyLongObject *v;
            unsigned long abs_ival;
            unsigned long t;  /* unsigned so >> doesn't propagate sign bit */
            int ndigits = 0;
            int sign;
        
            if (IS_SMALL_INT(ival)) {
                return get_small_int((sdigit)ival);
            }
        
            if (ival < 0) {
                /* negate: can't write this as abs_ival = -ival since that
                    invokes undefined behaviour when ival is LONG_MIN */
                abs_ival = 0U-(unsigned long)ival;
                sign = -1;
            }
            else {
                abs_ival = (unsigned long)ival;
                sign = ival == 0 ? 0 : 1;
            }
        
            /* Fast path for single-digit ints */
            if (!(abs_ival >> PyLong_SHIFT)) {
                v = _PyLong_New(1);
                if (v) {
                    Py_SET_SIZE(v, sign);
                    v->ob_digit[0] = Py_SAFE_DOWNCAST(
                        abs_ival, unsigned long, digit);
                }
                return (PyObject*)v;
            }
        
        #if PyLong_SHIFT==15
            /* 2 digits */
            if (!(abs_ival >> 2*PyLong_SHIFT)) {
                v = _PyLong_New(2);
                if (v) {
                    Py_SET_SIZE(v, 2 * sign);
                    v->ob_digit[0] = Py_SAFE_DOWNCAST(
                        abs_ival & PyLong_MASK, unsigned long, digit);
                    v->ob_digit[1] = Py_SAFE_DOWNCAST(
                            abs_ival >> PyLong_SHIFT, unsigned long, digit);
                }
                return (PyObject*)v;
            }
        #endif
        
            /* Larger numbers: loop to determine number of digits */
            t = abs_ival;
            while (t) {
                ++ndigits;
                t >>= PyLong_SHIFT;
            }
            **v = _PyLong_New(ndigits);**
            if (v != NULL) {
                digit *p = v->ob_digit;
                Py_SET_SIZE(v, ndigits * sign);
                t = abs_ival;
                while (t) {
                    *p++ = Py_SAFE_DOWNCAST(
                        t & PyLong_MASK, unsigned long, digit);
                    t >>= PyLong_SHIFT;
                }
            }
            return (PyObject *)v;
        }
        ```
        
    - _PyLong_New
        
        ```c
        // Objects/longobject.c
        PyLongObject *
        _PyLong_New(Py_ssize_t size)
        {
            PyLongObject *result;
            /* Number of bytes needed is: offsetof(PyLongObject, ob_digit) + sizeof(digit)*size.
                Previous incarnations of this code used sizeof(PyVarObject) instead of the offsetof, 
                but this risks being incorrect in the presence of padding between the PyVarObject header and the digits. */
            
            // 고정된 길이가 MAX_LONG_DIGITS 보다 작은지 확인
            if (size > (Py_ssize_t)MAX_LONG_DIGITS) {
                PyErr_SetString(PyExc_OverflowError,
                                "too many digits in integer");
                return NULL;
            }
            
            // ob_digit 길이에 맞춰 메모리 재할당
            result = PyObject_MALLOC(offsetof(PyLongObject, ob_digit) +
                                        size*sizeof(digit));
            if (!result) {
                PyErr_NoMemory();
                return NULL;
            }
            **return (PyLongObject*)PyObject_INIT_VAR(result, &PyLong_Type, size);**
        }
        ```
                    

## 11.5 유니코드 문자열 타입

### 11.5.1 사전 지식

[https://velog.io/@viiviii/1-ASCII-ISO-8859-Unicode의-탄생](https://velog.io/@viiviii/1-ASCII-ISO-8859-Unicode%EC%9D%98-%ED%83%84%EC%83%9D)

### 11.5.2 파이썬 문자 인코딩

- char 타입에서 사용하는 ASCII의 문제
    - 1byte로, 전세계에서 사용하는 모든 문자, 이모지 등을 담기엔 용량 및 크기가 부족합니다.
- 유니코드 문자 데이터베이스(UCD, Unicode Character Database) 도입
    - 128개의 문자만 포함하는 ASCII와 달리 143,859 개의 문자를 포함하고 있습니다. (version 13 기준)
    - 국제 문자 세트(UCS, Universal Character Set)란 문자 테이블로 모든 문자를 정의하며, 테이블의 각 문자는 **코드 포인트**라는 16진법 고유 식별자를 가집니다.
    - 코드 포인트를 **이진값으로 변환**하기 위해 다양한 인코딩을 지원합니다.
- CPython 유니코드 문자열이 처리하는 것은 인코딩 뿐
    - 코드 포인트를 올바른 스크립트로 나타내는 것은 운영 체제의 책임입니다.
    - CPython은 UCD 사본을 포함하고 있지 않기 때문에 유니코드 표준이 변경될 때마다 CPython을 업데이트하지 않아도 됩니다.

파이썬 유니코드 문자열은 다양한 플랫폼을 지원하기 위해 1byte, 2byte, 4byte 3가지 길이의 인코딩을 지원합니다.
인코딩 방법으로는 **UTF-8을 가장 일반적으로 사용**합니다. ASCII 호환성은 인코딩 메커니즘을 결정할 때 중요한 요소인데, UTF-8은 **ASCII와 호환**되기 때문입니다.
    

### 11.5.3. 확장 문자 타입

CPython 소스 코드에서 인코딩 방식을 알 수 없는 유니코드 문자열을 처리할 경우, C 타입 wchar_t 가 사용됩니다. 유니코드 문자열 객체는 wchar_t 타입의 상수를 문자열 객체로 변환하는 PyUnicode_FromWideChar() 함수를 제공합니다.

> wchar_t: 확장 문자를 사용하는 문자열을 위한 C 표준

예를 들어, python -c 를 실행할 때 사용되는 pymain_run_command()가 PyUnicode_FromWideChar()를 사용해 -c 인수를 유니코드 문자열로 변환합니다.

```c
// Modules ▶︎ main.c 225행
static int
pymain_run_command(wchar_t *command, PyCompilerFlags *cf)
{
    PyObject *unicode, *bytes;
    int ret;

    unicode = PyUnicode_FromWideChar(command, -1);
...
```

### 11.5.4. 바이트 순서 표식

파일 등의 입력을 디코딩할 때, CPython은 바이트 순서 표식(byte order mark, BOM)을 보고 바이트 순서를 인식합니다.

- BOM은 유니코드 바이트 스트림의 시작 부분에 나타나는 특수 문자로, 수신자에게 이 스트림에 어떤 바이트 순서로 데이터가 저장됐는지 알려줍니다.
    - 컴퓨터 시스템에 따라 인코딩 시 바이트 순서도 다를 수 있습니다.
    - 올바른 인코딩을 사용하더라도 잘못된 바이트 순서를 사용하면 데이터가 망가집니다.
    - CPython의 기본 바이트 순서는 전역 변수 sys.byteorder 에 설정됩니다. (little, big 등)

### 11.5.5 encodings 패키지

- Lib ▶︎ encodings의 encodings 패키지는 CPython을 위해 100개 이상의 인코딩을 기본으로 지원합니다.
    - 문자열 또는 바이트 문자열의 .encode() / .decode() 메서드는 호출될 때마다 이 패키지에서 인코딩을 검색합니다.
- 각 인코딩은 별도 모듈로 정의되어 있습니다.
- 모든 인코딩 모듈은 getregentry()라는 함수를 정의하고 다음 특성들을 구현합니다.
    - 인코딩의 고유한 이름
    - 코덱 모듈로부터 가져온 해당 인코딩의 인코딩/디코딩 함수
    - 증분 인코더와 디코더 클래스
    - 스트림 방식의 reader/writer 클래스
- 대부분의 인코딩 모듈은 codecs나 _multibytecode 모듈의 동일한 코덱을 공유합니다. 일부 인코딩 모듈은 Modules ▶︎ cjkcodes의 별도 C 코덱 모듈을 사용하기도 합니다.
    - 유니코드 이외의 인코딩들은 유니코드 문자열 객체 구현과 분리된 Modules ▶︎ _codecs에 구현돼 있습니다.

### 11.5.6 코덱 모듈과 구현, 내부 코덱

- codecs 모듈은 데이터를 특정 인코딩으로 변환합니다.
- 유니코드 객체 구현 (Objects/unicodeobject.c)에 포함된 인코딩 method 목록
    - ascii: `PyUnicode_EncodeASCII()`
    - latin1: `PyUnicode_EncodeLatin1()`
    - UTF7: `PyUnicode_EncodeUTF7()`
    - UTF8: `PyUnicode_EncodeUTF8()`
    - UTF16: `PyUnicode_EncodeUTF16()`
    - UTF32: `PyUnicode_EncodeUTF32()`
    - unicode_escape: `PyUnicode_EncodeUnicodeEscape()`
    - raw_unicode_escape: `PyUnicode_EncodeRawUnicodeEscape()`
- 내부 인코딩들은 CPython의 고유한 특성으로 일부 표준 라이브러리 함수와 소스 코드 작성에 유용하게 사용됩니다.
- 텍스트 인코딩 목록
    - idna: RFC 3490 구현
    - mbcs: ANSI 코드페이지에 따라 인코딩 (Windows 전용)
    - raw_unicode_escape: python 소스 코드 저수준 리터럴을 문자열로 변환
    - undefined: 기본 시스템 인코딩 시도
    - unicode_escape: 데이터를 python 소스 코드에 적합한 유니코드 리터럴로 변환
- 이진 데이터용 인코딩 목록
    - base64_codec (base64, base-64): 데이터를 MIME base64 형식으로 변환
    - bz2_codec (bz2): 문자열을 bz2로 압축
    - hex_codec (hex): byte 당 2자리 숫자를 사용 -> 데이터를 16진법으로 표현
    - quopri_codec (quoted-printable): 데이터를 MIME QP(Quoted-Printable) 형식으로 변환
    - rot_13 (rot13): Ceaser-cypher 적용한 결과물 반환
    - uu_codec (uu): uuencode 사용하여 변환
    - zlib_codec (zip, zlib): gzip 사용하여 데이터 압축
    

## 11.6 Dictionary 타입

- 지역•전역 변수 저장이나 키워드 인자 전달 등 많은 곳에서 사용됩니다.
- 매핑된 값만 저장하는 해시 테이블 덕에 매우 컴팩트 합니다.
- 내장 불변 타입들의 일부인 해싱 알고리즘이 매우 빠른 덕에 빠른 속도를 제공합니다.

### 11.6.1 해싱

- 모든 internal immutable type(내장 불변 타입)은 해시 함수를 제공합니다.
    - tp_hash 타입 슬롯에 정의되어 있습니다.
    - 사용자 지정 타입의 경우 매직 메서드 __hash__()를 사용해 해시 함수를 정의합니다.
    - 해시값은 포인터와 크기가 동일합니다. (64비트 시스템에선 64비트, 32비트 시스템에선 32비트, ...)
    - 해시값이 해당 값의 메모리 주소를 의미하진 않습니다.
- 해시 충돌이 있으면 안됩니다.
    - 파이썬 객체의 해시값은 객체의 수명이 지속되는 동안 변하는 일이 없어야 합니다.
    - 불변 인스턴스의 경우 값이 동일한 두 불변 인스턴스의 해시는 같아야 합니다.
- 유니코드 문자열은 문자열의 바이트 데이터를 Python▶︎pyhash.c 모듈의 _Py_HashBytes()로 해시합니다.


### 11.6.2 딕셔너리의 구조

![pydictobject](../images/11_object_and_type/pydictobject.png)

- 딕셔너리의 크기, 버전 태그, 키와 값을 담고 있는 property들로 구성되어 있습니다.
- PyDictKeysObject: 키와 각 키 엔트리의 해시값을 담고 있는 딕셔너리 키 테이블 객체
- PyDictKeysObject property 목록
    - dk_entries (PyDictKeyEntry[]): 동적 할당된 dictionary key 엔트리 배열
    - dk_indices (char[]): 해시 테이블 - dk_entries 맵핑
    - dk_lookup (dict_lookup_func): 검색 함수
    - dk_nentries (Py_ssize_t): 엔트리 테이블의 엔트리를 사용한 개수
    - dk_refcnt (Py_ssize_t): reference counter
    - dk_size (Py_ssize_t): 해시 테이블 크기
    - dk_usable (Py_ssize_t): 엔트리 테이블에서 사용 가능한 엔트리 개수 (남은 엔트리 0개일 때 딕셔너리 크기 조정됨)
- PyDictObject property 목록
    - ma_keys (PyDictKeysObject*): 딕셔너리 키 테이블 객체
    - ma_used (Py_ssize_t): 딕셔너리 내 항목 개수
    - ma_values (PyObject**): 추가된 값 배열
    - ma_version_tag (uint64_t): 딕셔너리 버전


### 11.6.3 검색

- 주어진 키 객체로 딕셔너리 항목을 찾을 때 범용 검색 함수 lookdict()를 사용합니다.
- 딕셔너리 검색이 처리해야 하는 3가지 시나리오
    1. 주어진 key 의 memory address 를 key table 에서 찾을 수 있는 경우
    2. 주어진 key object 의 hash value 를 key table 에서 찾을 수 있는 경우
    3. dictionary 에 해당 key 가 없는 경우
- 검색 함수의 항목 탐색 순서
    1. ob의 hash value를 구합니다.
    2. dictionary key 중 ob의 hash value 와 일치하는 값을 찾아 인덱스(ix)를 구합니다.
    3. ix 값이 비어있을 경우, DKIX_EMPTY를 반환합니다.
    4. 주어진 index로 key entry ep를 찾습니다.
    5. ob와 key의 값이 일치하면 ob는 key 와 동일한 값을 가리키는 pointer이기 때문에 찾은 값을 반환합니다.
    6. ob의 hash와 key의 hash가 일치할 때도 찾은 값을 반환합니다.
    

## References

- [https://docs.python.org/3/c-api/structures.html](https://docs.python.org/3/c-api/structures.html)
- [https://docs.python.org/3.9/reference/datamodel.html](https://docs.python.org/3.9/reference/datamodel.html)
(한국어 버전: [https://docs.python.org/ko/3.9/reference/datamodel.html](https://docs.python.org/ko/3.9/reference/datamodel.html))
- [https://docs.python.org/3.9/c-api/typeobj.html](https://docs.python.org/3.9/c-api/typeobj.html)
