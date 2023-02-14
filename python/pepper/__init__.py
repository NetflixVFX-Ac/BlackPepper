"""
*** What is pepper ? ***
    > 이 모듈은 kitsu의 python rest full API(Gazu)를 활용하여 \n
    path를 추출하는 kitsu 매핑 API 이다. \n
    FX 템플릿을 각 템플릿이 캐스팅된 샷에 일괄적으로 적용한 뒤 모든 샷의 pre-render을 실행,
    pre-comp 영상을 받아 아티스트가 FX의 pre-viz를 볼 수 있다.\n
    FX template를 pre-comp하기 위해 생성된 후디니 씬파일은 각 샷의 working file로, mov파일은 output file이 된다.\n

*** How to use pepper ? ***
    *Login
        먼저 호스트를 지정해주고, identify와 password 를 이용해 로그인한다. \n
        ex) self.pepper = Houpub() \n
        self.pepper.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy") \n

    *get working file path and output file path
        사용자가 원하는 project의 working file path를 얻고 싶다면  asset 혹은 shot의 task, task type 그리고 software 정보를
        입력하면 local경로에 존재하는 path를 얻을 수 있다. output file path의 경우는 현재 last revision에서 다음 버전을 체크하고
        확장자를 추가하여 local경로에 존재하는 path를 얻을 수 있다.

    *about casting
        asset이 casting한 shot의 정보를 알 수 있고 shot은 casting된 asset의 정보를 보여준다.
        working file 및 output file이 없을 경우 정보를 알 수 없다.

***** License Copyright *****

Netflix Academy 1st class Team Hook

This API was created in the first season of the Netflix Academy \n
and was created during the team project period by the Hook team.
"""
