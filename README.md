# CPython-Guide jupyter-book 작업 가이드

jupyter-book github page 접속 주소: https://pseudo-lab.github.io/CPython-Guide

1. 저장소를 fork 합니다.

   ```
   Pseudo-Lab/CPython-Guide
   ```

2. 작업을 진행합니다.

   ```
   git clone https://github.com/Pseudo-Lab/CPython-Guide.git
   ```

3. pull request를 날립니다.

   ```
   git clone https://github.com/Pseudo-Lab/CPython-Guide
   ```

4. pull request 승인 후 push가 완료되면 자동으로 빌드됩니다.

5. change the contents in `book/docs` folder with the contents from your studies

6. configure `_toc.yml` file

7. build the book using Jupyter Book command

   ```
   jupyter-book build 2021-Kaggle-Study/book
   ```

8. sync your local and remote repositories

   ```
   cd 2021-Kaggle-Study
   git add .
   git commit -m "adding my first book!"
   git push
   ```

9. Publish your Jupyter Book with Github Pages

   ```
   ghp-import -n -p -f book/_build/html -m "initial publishing"
   ```
