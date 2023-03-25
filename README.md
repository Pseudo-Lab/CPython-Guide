# CPython-Guide jupyter-book 작업 가이드

jupyter-book github page 접속 주소: https://pseudo-lab.github.io/CPython-Guide

1. 저장소를 fork 합니다.

   ```
   Pseudo-Lab/CPython-Guide
   ```

2. 저장소 및 python 패키지를 받습니다.

   ```bash
   git clone https://github.com/[작업자의 Github아이디]/CPython-Guide.git
   cd [CPython-Guide 폴더]  # 윈도우즈 command line의 /d 옵션도 같이
   pip install -r requirements.txt  # jupyter-book 패키지 설치, ghp-import는 꼭 설치안해도됨. (git action용)
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

5. pull request 승인 후 push가 완료되면 자동으로 사이트가 빌드됩니다.



# jupyter-book 작업 구조
```yaml
CPython-Guide
├── .github                #  git action workflow가 있습니다.
├── book                   #  문서 메인 폴더 입니다.
│   ├── docs               #  문서가 모여있는 폴더입니다.
│   ├── images             #  문서에 들어가는 이미지 폴더입니다.
│   ├── _config.yml        #  github page config 입니다.
│   ├── _toc.yml           #  문서 레이아웃 구성 파일 입니다.
│   ├── intro.md           #  문서의 시작 페이지 파일 입니다.
├── README.md
├── requirements.txt
└── .gitignore
```
문서는 book/docs 폴더에 추가하고 작성합니다.
_toc.yml에 문서를 등록해야 페이지에 보입니다.

# 파일명 규칙
1. docs: 챕터번호_섹션번호_문서제목  
   (0_0_dev_env_setup.md, 0_1_directory_structure.md, 챕터 최상단은 0번 섹션으로 처리)
2. images: 챕터폴더/사진순서(두자리)_사진내용  
   (0_dev_env_setup/00_vscode_plugin.png, 0_dev_env_setup/01_tasks_explorer_result.png)


# 로컬에서 빌드한 페이지가 조금 이상할 때
_build 폴더를 삭제 후 다시 빌드합니다. 이전 빌드 결과물에 대한 잔여물이 남는 케이스입니다.