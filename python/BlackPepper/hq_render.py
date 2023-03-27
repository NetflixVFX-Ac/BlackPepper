import hou
# import hqueue

job_name = "sw_toy_test_job"
file_path = "/home/rapa/hq_toy.hiplc"
new_file_path = "/home/rapa/hq_toy_2.hiplc"
hq_sever = "192.168.3.103:5000"
hq_hfs = "/opt/hfs19.5.493"
hq_driver = "/out/mantra_ipr"
render_settings = {
    "hq_driver": "/out/mantra_ipr",
    "hq_frames": "1-10",
    "hq_outputpicture": "render.$F4.exr"
}

class Hqrender:
    def submit_hqueue_job(job_name, hip_file):
        """
        HQueue 작업을 제출하는 함수
        :param job_name: 작업 이름
        :param hip_file: 작업을 수행 할 hip 파일 경로
        :param render_settings: 렌더링 설정
        """
        # HQueue Render 노드 생성
        hou.hipFile.load(file_path)
        hqueue_node = hou.node("/out").createNode("hq_render")

        # 작업 이름 설정
        hqueue_node.parm("hq_job_name").set(job_name)

        # hip 파일 설정
        hqueue_node.parm("hq_hip").set(hip_file)

        hqueue_node.parm("hq_driver").set(hq_driver)
        # hqueue_node.parm("hq_sever").set(hq_sever)
        # hqueue_node.parm("hq_hfs").set(hq_hfs)

        # 렌더링 설정 설정
        # for key, value in render_settings.items():
        #     hqueue_node.parm(key).set(value)

        # HQueue에 작업 제출
        # hqueue.submit(hqueue_node)
        # hou.hipFile.save(new_file_path)
        hqueue_node.parm("execute").pressButton()


    submit_hqueue_job(job_name, file_path)
    # hou.hipFile.save(new_file_path)






    def has_mantra_node(file_path):
        # Create a Houdini session
        hou.hipFile.load(file_path)

        # Get all nodes in the current scene
        nodes = hou.node('/').allSubChildren()

        # Check if there is at least one Mantra node
        for node in nodes:
            if node.type().name() == 'ifd':
                return True

        # If no Mantra node found, return False
        return False

    def get_mantra_node_info(file_path):
        # Create a Houdini session
        hou.hipFile.load(file_path)

        # Get all nodes in the current scene
        nodes = hou.node('/').allSubChildren()

        # Find the first Mantra node and return its information
        for node in nodes:
            if node.type().name() == 'ifd':
                node_info = {
                    'name': node.name(),
                    'type': node.type().name(),
                    'path': node.path(),
                    # 'parm_values': node.parmValues()
                }
            print(node.type().name()=='ifd')
            return node_info
        # If no Mantra node found, return None
        return None


# has_mantra_node(file_path)

# get_mantra_node_info(file_path)
