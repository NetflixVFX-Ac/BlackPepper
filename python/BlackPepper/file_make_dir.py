import os
import gazu
from BlackPepper.pepper import Houpub

gazu.set_host("http://192.168.3.116/api")
gazu.log_in("pipeline@rapa.org", "netflixacademy")

project = gazu.project.get_project_by_name("BLACKPEPPER")


def set_file_tree():
    """self.project의 file tree를 업데이트 해준 뒤 file tree 변경 로그를 저장한다. \n
    self.project가 없을 시 작동하지 않는다.

    Examples:
        BlackPepper.set_file_tree('mnt/projects', 'hook')

    Args:
        mount_point(str): Local mountpoint path
        root(str): Root directory for local kitsu path

    Raises:
        Exception: If self.project don't exist, and if input is not string that leads to local path
    """
    file_tree = {
        "working": {
            "mountpoint": '/mnt/project',
            "root": 'hook',
            "folder_path": {
                "shot": "<Project>/shots/<Sequence>/<Shot>/<TaskType>/working/v<Revision>",
                "asset": "<Project>/assets/<AssetType>/<Asset>/<TaskType>/working/v<Revision>",
                "style": "lowercase"
            },
            "file_name": {
                "shot": "<Project>_<Sequence>_<Shot>_<TaskType>_<Revision>",
                "asset": "<Project>_<AssetType>_<Asset>_<TaskType>_<Revision>",
                "style": "lowercase"
            }
        },
        "output": {
            "mountpoint": '/mnt/project',
            "root": 'hook',
            "folder_path": {
                "shot": "<Project>/shots/<Sequence>/<Shot>/<TaskType>/output/<OutputType>/v<Revision>",
                "asset": "<Project>/assets/<AssetType>/<Asset>/<TaskType>/output/<OutputType>/v<Revision>",
                "style": "lowercase"
            },
            "file_name": {
                "shot": "<Project>_<Sequence>_<Shot>_<OutputType>_v<Revision>",
                "asset": "<Project>_<AssetType>_<Asset>_<OutputType>_v<Revision>",
                "style": "lowercase"
            }
        }
    }
    gazu.files.update_project_file_tree(project, file_tree)

    # for asset in gazu.asset.all_assets_for_project(project):
    #     print(asset)
    #     for task in gazu.task.all_tasks_for_asset(asset):
    #         print('task :', task)
    #         path = os.path.dirname(gazu.files.build_working_file_path(task))
            # os.makedirs(path)

    # for shot in gazu.shot.all_shots_for_project(project):
    #     print(shot)
    #     for task in gazu.task.all_tasks_for_shot(shot):
    #         path = os.path.dirname(gazu.files.build_working_file_path(task))
            # out_path = os.path.dirname(gazu.files.build_entity_output_file_path)
            # os.makedirs(path)

    # for shot in gazu.shot.all_shots_for_project(project):
    #     for task_type in gazu.task.all_task_types_for_shot(shot):
    #         output_cam = gazu.files.get_output_type_by_name('movie_file')
    #         path = os.path.dirname(gazu.files.build_entity_output_file_path(shot, output_cam, task_type))
    #         print(path)
            # os.makedirs(path)

    # for shot in gazu.shot.all_shots_for_project(project):
    #     aaa = gazu.task.get_task_type_by_name('fx')
    #     bbb = gazu.files.get_output_type_by_name('jpg_sequence')
    #     ccc = gazu.files.get_last_entity_output_revision(shot, bbb, aaa)
    #     # gazu.files.new_entity_output_file(shot, bbb, aaa, 'start')
    #     ddd = gazu.files.get_last_entity_output_revision(shot, bbb, aaa)
    #     print(ccc, ddd)

def publish_output():
    pepper = Houpub()
    pepper.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy")
    pepper.software = 'hipnc'
    pepper.project = 'BLACKPEPPER'
    aaa = gazu.shot.all_shots_for_project(pepper.project)
    # print(aaa)
    for shot in aaa:
        print(shot)

    pepper.sequence = 'SQ01'
    pepper.shot = '0010'
    pepper.entity = 'shot'
    # pepper.publish_output_file('FX', 'Movie_file', "first_output")
    print(pepper.make_next_output_path('camera_cache', 'layout_camera'))

def casting_create(self, nb):
    asset_castings = gazu.casting.get_shot_casting(self.shot)
    new_casting = {"asset_id": self.asset['id'], "nb_occurences": nb}
    asset_castings.append(new_casting)
    gazu.casting.update_shot_casting(self.project, self.shot, casting=asset_castings)

def main():
    # set_file_tree()
    publish_output()
    # pass



if __name__ == "__main__":
    main()