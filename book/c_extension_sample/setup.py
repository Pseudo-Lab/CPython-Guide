from distutils.core import setup, Extension

def main():
    setup(name="fputs",
          version="1.0.0",
          description="Python interface for the fputs C library funtion",
          author="kwang1",
          author_email="4roring@naver.com",
          ext_modules=[Extension("fputs", ["fputsmodule.c"])])


if __name__ == "__main__":
    main()
