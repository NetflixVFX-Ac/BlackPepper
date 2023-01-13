import sys
# import re

to_do_list=[]
last_num=1

def print_help():
    return '''
    To-do list를 작성해보세요.
    '''


def todo_add():  
    task=input("Enter a task to add :")
    add_task=task

    # if "to_do" not in to_do_list:
    #     to_do_list["to_do"]=[]
    to_do_list.append(add_task)

    main()

def todo_show():
    for index, value in enumerate(to_do_list):
        print(str(index+1)+".",value)

    main()

def todo_edit():
    task=input("Enter a task to done :")
    done_task=task+" ✓"
    to_do_list[to_do_list.index(task)]=done_task


    # for i in to_do_list:
        # done_task=re.sub(task,task+" ✓",i)

    # if delete_task in to_do_list["to_do"]:
    #     del(to_do_list["to_do"])
    # print("edit_task")

    main()


def todo_archive():
    print("check_tast")


def main():
    print(print_help())
    
    # args=sys.argv
    # for str_arg in args[1:]:
    #     todo_add(str_arg)

    to_do=input("Enter a command (add,list,edit,archive,end) :")
    if to_do=='add':
        todo_add()
    elif to_do=='list':
        todo_show()
    elif to_do=='edit':
        todo_edit()
    elif to_do=='archive':
        todo_archive()
    elif to_do=='end':
        exit()
    else:
        print("올바른 명령어를 입력하세요.")
        main()
    


if __name__=="__main__":
    main()




