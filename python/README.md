# What is Black Pepper
Black Pepper is FX templates 에 캐스팅된 샷들을 jpg,mov render를  자동화 해주는 API 이다.

* Target User :  FX artist
* FX artist 가 template asset fx 에 casting 된 많은 샷들을 Houdini 에서 pre-comp 와 mantra 에서 jpg 로 render 하고
ffmfeg 을 사용하여 jps sequnce 들을 mov 로 자동화한다. 많은 샷들의 FX 룩을 보기 위한 API 이다.  

***
### kitsu & gazu ?
* kitsu는 VFX 스튜디오 제작관리 web application 이고
* Gazu 는 Kitsu API용 Python 클라이언트 이다.
  * Gazu 를 사용하면  Kiust'에서 쉽게 데이터를 가져올 수 있다.

***
## Kitsu & Gazu links:

* kitsu URL : https://github.com/cgwire/kitsu

* Gazu URL : https://github.com/cgwire/gazu
***
## Getting Started

## Black Pepper Download links:

* SSH clone URL: ssh://git@git.jetbrains.space/pipeline/main/hook.git

* HTTPS clone URL: https://git.jetbrains.space/pipeline/main/hook.git

# How to use Black Pepper

*
*
*






***
##  Black Pepper included APIs

* pepper
* auto_login
* MVC (model, view, controller)
* houpepper
* render_process_bar
* ffmpeg_process_bar
***
## UI 구성 

#### UI 는 총 4개의 window 로 구성되어있다.

* login window 

![login](./img/login.png)

* main window

![main](./img/main.png)
* Progress window

![progress](./img/progress.png)

Render Check List & Full Path
![path](./img/path.png)


## Login

```
최초 1회 로그인시 자동 로그인이 된다.
다른 아이디로 로그인 하고싶으면 메인 창에서 메뉴바의 User 에서 Logout 또는 
 
```
***
## FileTree
<pre>
Examples

├── blackpepper
│   ├── assets
│   │   └── fx_template
│   │       ├── temp_breaking_glass
│   │       │   └── simulation
│   │       │       └── working
│   │       │           └── v001
│   │       │               └── blackpepper_fx_template_temp_breaking_glass_simulation_001.hipnc
│   │       ├── temp_dancing_particle
│   │       │   └── simulation
│   │       │       └── working
│   │       │           └── v001
│   │       │               └── blackpepper_fx_template_temp_dancing_particle_simulation_001.hipnc
│   │       └── temp_fire
│   │           └── simulation
│   │               └── working
│   │                   └── v001
│   │                       └── blackpepper_fx_template_temp_fire_simulation_001.hipnc
│   └── shots
│       └── sq01
│           ├── 0010
│           │   ├── fx
│           │   │   ├── output
│           │   │   │   ├── jpg_sequence
│           │   │   │   │   ├── v001
│           │   │   │   │   ├── v002
│           │   │   │   │   └── v003
│           │   │   │   │       └── blackpepper_sq01_0010_v003_####.jpg
│           │   │   │   └── movie_file
│           │   │   │       ├── v001
│           │   │   │       ├── v002
│           │   │   │       │   └── blackpepper_sq01_0010_movie_file_v002.mov
│           │   │   │       └── v003
│           │   │   │           └── blackpepper_sq01_0010_movie_file_v003.mov
│           │   │   └── working
│           │   │       ├── v001
│           │   │       ├── v002
│           │   │       └── v003
│           │   │           └── blackpepper_sq01_0010_fx_003.hipnc
│           │   └── layout_camera
│           │       └── output
│           │           └── camera_cache
│           │               ├── v000
│           │               └── v001
│           │                   └── blackpepper_sq01_0010_camera_cache_v001.abc
│           ├── 0020
│           │   ├── fx
│           │   │   ├── output
│           │   │   │   ├── jpg_sequence
.           .   .   .   .
.           .   .   .   .
.           .   .   .   .
</pre>
## Save Data

### user.json
#### 로그인시 로그인 정보들과 render 시 recent render files list 정보들은 json path에 자동 저장되고
render files list 를 save list 버튼을 통해 커스텀 저장할수 있다.
```
json save path : <root>/hook/BlackPepper/.config/user.json
```
## log
#### 아래의 항목들은 log save path 에 log 기록을 남긴다.
* 로그인 시 로그인 정보
* file tree update
* working & output file Publish
```
log save path : <root>/hook/BlackPepper/.config/hook_login.log
```
***
## Log
#### 로그가 기록 되는 것
* 로그인 시 로그인 정보
* file tree update
* working & output file Publish

***
# License Copyright

## Netflix Academy 1st class Team Hook

### This API was created in the first season of the Netflix
### Academy and was created during the team project period by the Hook team.