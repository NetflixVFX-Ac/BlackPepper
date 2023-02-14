import logging


def make_logger(name):
    """1. logger instance를 만든다.\n2. logger의 level을 가장 낮은 수준인 DEBUG(자세한정보)로 설정\n3. formatter 지정
    asctime - name - levelname - message
    \n4. handler instance (StreamHandler,FileHandler)생성
    \n5. StramHandler:INFO,FileHandler:DEBUG 으로 level 설정
    \n6. handler 출력 format 지정 \n7. logger에 handler 추가

        지정된 name 의 로거를 반환하고, 이름을 지정하지 않으면 root 로거를 반환합니다.
    Return a logger with the specified name, creating it if necessary.
    If no name is specified, return the root logger.\n\n

    \n Logger : 어플리케이션 코드가 직접 사용할 수 있는 인터페이스를 제공함.
    \n Handler : logger 에 의해 만들어진 log 기록들을 적합한 위치로 보냄
    \n StreamHandler : 콘솔창에 로그 메시지 출력\n
    \n FileHandler : 로깅 메세지를 파일로 저장 filename="pepper.log"
    \n Formatter : log 기록들의 최종 출력본의 레이아웃을 결정함

    Args:
        name(str): 이름을 지정 하지 않으면(None)  == root

    Returns:
        logger
    """
    name = str(name)

    # 1 logger instance를 만든다.
    logger = logging.getLogger(name)

    # 2 logger의 level을 가장 낮은 수준인 DEBUG로 설정해둔다.
    logger.setLevel(logging.DEBUG)

    # 3 formatter 지정
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # 4 handler instance 생성
    console = logging.StreamHandler()
    file_handler = logging.FileHandler(filename="pepper.log")

    # 5 handler 별로 다른 level 설정
    console.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    # 6 handler 출력 format 지정
    console.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 7 logger에 handler 추가
    logger.addHandler(console)
    logger.addHandler(file_handler)

    return logger
