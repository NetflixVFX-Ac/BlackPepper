import json

class Todolist:
    def __init__(self, todo_list, complete_list):
        self.todo_list = todo_list
        self.complete_list = complete_list
        
    def input_check(self, input_num):
        if input_num.isdigit() == True and int(input_num) <= len(self.todo_list):
            pass
        else:
            print("wrong input")
            self.task_loop()

    def task_input(self, addtask):
        self.todo_list.append(addtask)
        self.task_loop()

    def task_delete(self, input_num):
        input_num = int(input_num)
        self.todo_list.remove(self.todo_list[input_num - 1])
        self.task_loop()

    def task_edit(self, input_num, newdata):
        input_num = int(input_num)
        self.todo_list[input_num - 1] = newdata
        self.task_loop()
    
    def task_complete(self, input_num):
        input_num = int(input_num)
        self.complete_list.append(self.todo_list[input_num - 1])
        self.todo_list.remove(self.todo_list[input_num - 1])
        self.task_loop()
    
    def briefing(self):
        n = 1
        if len(self.todo_list) == 0:
            print('no task to do')
        else:
            print('Tasks to do')
            for i in self.todo_list:
                print(f'{n}. {i}')
                n += 1
        n = 1
        if len(self.complete_list) == 0:
            print('no task done')
        else:  
            print('Completed Task')
            for i in self.complete_list:
                print(f'{n}. {i}')
                n += 1
        print('press a to add, c to complete, d to delete, e to edit, q to quit')
        
    def task_loop(self):
        self.briefing()
        answer = input('press here : ')
        if answer in ['a', 'A', 'ㅁ']:
            addtask = input("Input next task : ")
            self.task_input(addtask)
        elif answer in ['d', 'D', 'ㅇ']:
            input_num = input("Input task number : ")
            self.input_check(input_num)
            self.task_delete(input_num)
        elif answer in ['c', 'C', 'ㅊ']:
            input_num = input("Input task number : ")
            self.input_check(input_num)
            self.task_complete(input_num)
        elif answer in ['e', 'E', 'ㄷ']:
            input_num = input("Input task number : ")
            self.input_check(input_num)
            editedtask = input("Input new task : ")
            self.task_edit(input_num, editedtask)
        elif answer in ['q', 'Q', 'ㅂ']:
            self.finish_list()
        else:
            print('wrong_input')
            self.task_loop()
            
    def finish_list(self):
        
        print('Completed Tasks')
        n = 1
        for i in self.complete_list:
            print(f'{n}. {i}')
            n += 1
        n = 1
        print('Incomplete Tasks')
        for i in self.todo_list:
            print(f'{n}. {i}')
            n += 1
        output_json = {'todo_list' : self.todo_list, 'complete_list' : self.complete_list}
        print(output_json)
        file_path = "/home/rapa/test.json"
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(output_json, file)
        quit()


file_path = input("inp : ")
with open(file_path, 'r') as file:
    data = json.load(file)
    tdl = (data["todo_list"])
    cpl = (data["complete_list"])
me = Todolist(tdl, cpl)
me.task_loop()

   
    # def input_todolist():
    #     parser = argparse.ArgumentParser()
    #     parser.add_argument('todo', type = str, help="일의 리스트를 입력 : ,로 구분하세요")
    #     parser.add_argument('urgency', type = str, help="가장 중요한 일을 입력하세요")
    #     args = parser.parse_args()
    #     todolist = args.todo
    #     most_urgent = args.urgency
    #     if most_urgent not in todolist:
    #         print("급한 일이 없습니다")
    #         most_urgent = ""
    #     todo_list = todolist.split(',')
    #     return todo_list, most_urgent
        
    # def task_loop(todo_list, most_urgent, clear_list):
    #     briefing(todo_list, most_urgent, clear_list)
    #     answer = input('여기에 입력 : ')
    #     print('\n', end="")
    #     if answer in ['a', 'A', 'ㅁ']:
    #         add_task(todo_list, most_urgent, clear_list)
    #     elif answer in ['d', 'D', 'ㅇ']:
    #         delete_task(todo_list, most_urgent, clear_list)
    #     elif answer in ['c', 'C', 'ㅊ']:
    #         clear_task(todo_list, most_urgent, clear_list)
    #     elif answer in ['e', 'E', 'ㄷ']:
    #         edit_task(todo_list, most_urgent, clear_list)
    #     elif answer in ['q', 'Q', 'ㅂ']:
    #         quit_program(todo_list, clear_list)
    #     else:
    #         wrong_input(todo_list, most_urgent, clear_list)

    # def briefing(todo_list, most_urgent, clear_list):
    #     print(f"\n할 일은 {todo_list}입니다")
    #     print(f"가장 급한 일은 {most_urgent}입니다\n")
    #     print("할 일을 추가하려면 a, 삭제하려면 d, 수정하고 싶으면 e, 일을 완료했다면 c를 입력하세요. 종료 시에는 q를 입력하세요.")

    # def add_task(todo_list, most_urgent, clear_list):
    #     new_task = input("새 작업을 입력하세요 : ")
    #     todo_list.append(new_task)
    #     task_loop(todo_list, most_urgent, clear_list)

    # def edit_task(todo_list, most_urgent, clear_list):
    #     tasknum = input("수정하고 싶은 작업 번호를 입력하세요 : ")
    #     if tasknum.isdigit() == True:
    #         tasknum = int(tasknum)
    #     else:
    #         print("숫자를 입력해야 합니다")
    #         task_loop(todo_list, most_urgent, clear_list)
    #     edited = input("수정 후 이름을 입력하세요 : ")
    #     edited = str(edited)
    #     todo_list[tasknum] = edited
    #     task_loop(todo_list, most_urgent, clear_list)
        
    # def delete_task(todo_list, most_urgent, clear_list):
    #     delete_task = input("삭제할 작업을 입력하세요 : ")
    #     if delete_task in todo_list:
    #         todo_list.remove(delete_task)
    #         task_loop(todo_list, most_urgent, clear_list)
    #     else:
    #         print("잘못된 값을 입력했습니다")
    #         task_loop(todo_list, most_urgent, clear_list)

    # def clear_task(todo_list, most_urgent, clear_list):
    #     cleared_task = input("완료한 작업을 입력하세요 : ")
    #     if cleared_task in todo_list:
    #         todo_list.remove(cleared_task)
    #         clear_list.append(cleared_task)
    #         task_loop(todo_list, most_urgent, clear_list)
    #     else:
    #         print("잘못된 값을 입력했습니다")
    #         task_loop(todo_list, most_urgent, clear_list)

    # def next_urgent_sel(todo_list, most_urgent, clear_list):
    #     next_urgent = input(("중요한 일을 완료했습니다. 다음 중요한 일을 입력하세요 : "))
    #     if next_urgent.isdigit() == True:
    #         next_urgent = int(next_urgent)
    #     else:
    #         print("숫자를 입력해야 합니다")
    #         next_urgent_sel(todo_list, most_urgent, clear_list)
    #     most_urgent = todo_list[next_urgent]
    #     task_loop(todo_list, most_urgent, clear_list)

    # def wrong_input(todo_list, most_urgent, clear_list):
    #     print("잘못된 값을 입력했습니다.")
    #     task_loop(todo_list, most_urgent, clear_list)

    # def quit_program(todo_list, clear_list):
    #     print("감사합니다.")
    #     print(todo_list)
    #     print(clear_list)
    #     quit()

    # def main():
    #     clear_list = []
    #     todo_list, most_urgent = input_todolist()
    #     task_loop(todo_list, most_urgent, clear_list)

    # if __name__ == "__main__":  
    #     main()
