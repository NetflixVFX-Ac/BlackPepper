"""
*** What is pepper ? ***
    > 이 모듈은 kitsu의 python rest full API(Gazu)를 활용하여 \n
    path를 추출하는 kitsu 매핑 API 이다. \n
    FX 템플릿을 각 템플릿이 캐스팅된 샷에 일괄적으로 적용한 뒤 모든 샷의 pre-render을 실행,
    pre-comp 영상을 받아 아티스트가 FX의 프리비즈를 볼 수 있게 한다.\n
    Houdini 멀티샷의 기초단계로 pre-comp를 하기 위해 생성된 후디니 씬파일은 각 샷의 working file로, mov파일은 output file이 된다.\n


*** How to use & Examples ***
    > pepper 사용법 과 예시

    1) Login
        : 먼저 호스트를 지정해주고, identify와 password 를 이용해 로그인한다. \n
        ex) self.pepper = Houpub() \n
        self.pepper.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy") \n
    2)
        : 각 task 에 워킹파일 path 아웃풋 파일 path
        houdini template이 저장 될 working file path 정보를 얻는다. \n
        ex)

    3)
        : cam, asset 파일을 기존 working hip파일에 적용 \n
        ex)

    4)
        : 부가적으로 shots마다 cating된 template를 체크 \n
        ex)

        test_01.hip의 working file template에 cam, asset을 적용해서 새로운 exr, hip, mov를 outputfile로 만든다.
hip파일의 경우는 test_02.hip이라는 형식으로 outputfile이자 새로운 revision의 working file을 만든다.




*** Waht is log_pepper ***
    : pepper 를 위한 logger 모듈이다.\n
    * 퍼블리시하는 publish_working_file,publish_output_file \n
    이 두 함수를 사용 할 때 마다 로그인한 사용자의 이름과 debug 메세지를 정해진 logger(log_pepper)에 따라 log기록을 한다. \n
    * set_file_tree 함수는 self.project의 File tree를 업데이트 해준 뒤 File tree 변경 로그를 저장한다.\n
    self.project가 없을 시 작동하지 않는다.



*** License Copyright ***

Netflix Academy 1st class Team Hook

This API was created in the first season of the Netflix Academy \n
and was created during the team project period by the Hook team.

"""
