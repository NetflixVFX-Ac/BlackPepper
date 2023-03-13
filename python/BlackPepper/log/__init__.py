"""
*** logging ***
    : BlackPepper 에 기록을 위한 logger 모듈이다.\n
    * Auto login을 할 때 사용자가 로그인에 성공하였는지 결과를 log에 남긴다. \n
    host에 사용자의 id로 로그인이 잘 했는지 남겨준다.
    * 퍼블리시하는 publish_working_file,publish_output_file \n
    이 두 함수를 사용 할 때 마다 로그인한 사용자의 이름과 debug 메세지를 정해진 logger(log_pepper)에 따라 log기록을 한다. \n
    * set_file_tree 함수는 self.project의 File tree를 업데이트 해준 뒤 File tree 변경 로그를 저장한다.\n
    self.project가 없을 시 작동하지 않는다.
"""