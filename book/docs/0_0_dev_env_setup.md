# CPython 개발 환경 세팅
CPython-Guide는 CPython 파헤치기 책과 동일한 python3.9 버전을 기반으로 진행됩니다.

## CPython git 저장소 받기
```bash
git clone --branch 3.9 https://github.com/python/cpython.git
```
저장소를 받은 후 Visual Studio Code로 해당 폴더를 열어줍니다.

## Visual Studio Code 개발 환경 세팅
![VSCode 설치 플러그인](../images/0_dev_env_setup/00_vscode_plugin.png)
위 플러그인들을 설치합니다.

## task.json 작성
```json
{
	"version": "2.0.0",
	"tasks": [
		{
			"label": "build",
			"type": "shell",
			"group": {
				"kind": "build",
				"isDefault": true
			},
			"windows": {
				"command": "PCBuild/build.bat",
				"args": ["-p", "x64", "-c", "Debug"]
			},
            "linux": {
				"command": "make -j2 -s"
			},
            "osx": {
				"command": "make -j2 -s"
			}
		}
	]
}
```
.vscode/task.json 파일을 생성하고 위 내용을 작성합니다.  

![태스크 세팅 결과](../images/0_dev_env_setup/01_tasks_explorer_result.png)  
task.json 작성을 완료하면 TASK EXPLORER의 vscode 하위에 작성한 build task가 추가된 것을 볼 수 있습니다.

## launch.json 작성
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "msvc cl.exe debug cpython",
            "type": "cppvsdbg",
            "request": "launch",
            "program": "PCBuild/amd64/python_d.exe",
            "args": [],
            "stopAtEntry": false,
            "cwd": "${workspaceFolder}",
            "environment": [],
            "externalConsole": true,
            "preLaunchTask": "build"
        }
    ]
}
```
.vscode/launch.json 파일을 생성하고 위 내용을 작성합니다.  

이제 F5를 누르면 CPython 빌드 진행 및 디버깅을 할 수 있습니다.  
CPython의 진입점이 되는 Programs/python.c의 9번 라인에 디버그 브레이크를 걸고 실행해봅니다.
![CPyhton 디버깅](../images/0_dev_env_setup/02_cpython_debugging.png)  
위와 같이 디버깅 잡힌 것을 볼 수 있습니다.

개발환경 세팅은 여기까지입니다.

