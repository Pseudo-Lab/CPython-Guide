# CPython-Guide jupyter-book 작업 가이드

jupyter-book github page 접속 주소: https://pseudo-lab.github.io/CPython-Guide

1. 저장소를 fork 합니다.

   ```
   Pseudo-Lab/CPython-Guide
   ```

2. 저장소를 받습니다.

   ```bash
   git clone https://github.com/[작업자의 Github아이디]/CPython-Guide.git
   ```

3. 담당 페이지 작업을 진행합니다.  
그 후 빌드를 돌린 후 _build/html/index.html을 열어서 결과를 확인합니다.

   ```bash
   # 작업 root 경로 (working directory)가 CPython-Guide 최상위 경로인 경우.
   jupyter-book build ./book
   ```

4. 정상적으로 완료되었다면 pull request를 날립니다.

   ```bash
   # TODO: pull request 하는 방법 첨부 예정.
   ```

5. pull request 승인 후 push, merge가 완료되면 자동으로 빌드됩니다.



# jupyter-book 작업 구조
```Diff
CPython-Guide
├── .github                # 
├── book                   # 
│   ├── _build   
│   ├── docs
│   ├── _config.yml
│   ├── index.js
├── README.md
├── requirements.txt
└── .gitignore
```

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
