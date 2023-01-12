"""
2023년은 계묘년입니다.
년도를 적어서 60간지를 반환하는 프로그램을 만들어 보세요.

10간지: 갑을병정무기경신임계
12간지: 자축인묘진사오미신유술해

"""
def print_help():
    return '''
    입력 받은 년도를 60갑자로 출력해 주는 툴입니다.
    궁금하신 년도를 입력해 주세요!
    '''

def cal_year(data):
    
    list={
        '10간지':['경','신','임','계','갑','을','병','정','무','기'],
        '12간지':['신','유','술','해','자','축','인','묘','진','사','오','미']
    }
    

    first_year=list['10간지']
    second_year=list['12간지']

    first_word=first_year[data%10]
    second_word=second_year[data%12]

    print(f'    {data}년은 {first_word}{second_word}년입니다.')


def main(fail_count):

    try:
        print(print_help())
        year=input("    년도를 입력하세요: ")
        number=int(year)
        cal_year(number)
    except ValueError:
        print("------------------------------------------------------\n    왜 숫자가 아닌걸 입력하시나요. \n    현재까지 실패한 횟수:%d" %(fail_count))
        next_count=fail_count+1
        main(next_count)

if __name__ =="__main__":
    num=1
    main(num)
   
