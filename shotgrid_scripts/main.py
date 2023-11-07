# '''
# This is the in house Shotgrid Wrapper we use for anything Shotgrid related

# NOTE: If you want add any new elements or features add them in there

# Version:
#     - v1.0.0.4
# '''



import shotgun_api3
import os
from importlib import reload
import sys
import json
import traceback

absolute_path = os.path.dirname(__file__).split('\\')
del absolute_path[-2:]
dev_path = "/".join(absolute_path)
global_settings_path = os.path.join( dev_path, "utilities", "studio_global_settings")
sys.path.append( global_settings_path)

import global_settings
reload(global_settings)

## The Path to the Filters Folder
absolute_path2 = os.path.dirname(__file__).split('\\')
absolute_path2.append("filters")
filters_folder_path = "/".join(absolute_path2)
print("FILETERS: {}".format( filters_folder_path))


## Importing Global Settings
GLOBAL_SETTINGS = global_settings.GLOBAL_SETTINGS()

USER_DATA_NAME = GLOBAL_SETTINGS.ENV_USER_DATA_NAME





class Shotgrid_Utilites():
    def __init__(self, project_name):

        '''
            Arg:
                project_name:               The name of your project as it appears on Shotgrid
        '''
        ### Environment Variables you woul need to replace with you own
        self.GLOBAL_SHOT_TASK_TEMPLATE = GLOBAL_SETTINGS.GLOBAL_SHOT_TASK_TEMPLATE ## The global shot template
        self.GLOBAL_ASSET_TASK_TEMPLATE = GLOBAL_SETTINGS.GLOBAL_ASSET_TASK_TEMPLATE ## The Global Asset Template
        self.SHOTGRID_PROJECTS = GLOBAL_SETTINGS.SHOTGRID_PROJECTS



     
        self.sg = shotgun_api3.Shotgun("ADD YOUR SHOTGRID URL HERE",
                        login="ADD YOUR LOGIN INFORMATION HERE",
                        password="ADD PASSWORD INFORMATION HERE")



        ## Gets certain project data from the Global Settings
        ## Checks if the name given matches the projects on the server then gets the [ name ] and [ project id ]
        self.PROJECT_DATA = {}
        for projects in self.SHOTGRID_PROJECTS:
            if project_name == projects['name']:
                self.PROJECT_DATA["name"] = projects['name']
                self.PROJECT_DATA['id'] = projects['id']
            else:
                pass


 


        ##########################################################################################################
        ## Importing Shot Filters       
        with open("{}/shot_filters.json".format(filters_folder_path), 'r') as R:
                        self.ADDITIONAL_SHOT_FILTERS = json.load(R)

        with open("{}/asset_filters.json".format(filters_folder_path), 'r') as R:
                        self.ADDITIONAL_ASSET_FILTERS = json.load(R)

        with open("{}/sequence_filters.json".format(filters_folder_path), 'r') as R:
                        self.ADDITIONAL_SEQUENCE_FILTERS = json.load(R)

        with open("{}/task_filters.json".format(filters_folder_path), 'r') as R:
                        self.ADDITIONAL_TASK_FILTERS = json.load(R)

        with open("{}/user_filters.json".format(filters_folder_path), 'r') as R:
                        self.ADDITIONAL_USER_FILTERS = json.load(R)

        with open("{}/tag_filters.json".format(filters_folder_path), 'r') as R:
                    self.ADDITIONAL_TAG_FILTERS = json.load(R)

        with open("{}/tag_filters.json".format(filters_folder_path), 'r') as R:
            self.ADDITIONAL_TAG_FILTERS = json.load(R)

        with open("{}/project_filters.json".format(filters_folder_path), 'r') as R:
            self.ADDITIONAL_PROJECT_FILTERS = json.load(R)

        with open("{}/version_filters.json".format(filters_folder_path), 'r') as R:
            self.ADDITIONAL_VERSION_FILTERS = json.load(R)



    ######################################################################################################

    ###### ---------            create_Functions: Creating functions                        --------######

    ### These Functions Deal with Creating an Entitiy on Shotgrid, wheather a shot/asset , sequence ect

    ######################################################################################################

    def create_new_sequence(self, sequence_number):
        '''
            Create a Sequence without any shots
            This only creates the sequence entity, it has no shots with in it upon creating it
        '''

        if not type(sequence_number) == str:
            print( "\nERROR:......Sequence Number Argument needs to be a string, currently is a {}\n".format( type(sequence_number) ))
    
        else:

            self.sequence_number = sequence_number

            ## Creating the Shotgrid Data
            sequence_data = {
                'project': { "type":"Project", 
                            "id": self.PROJECT_DATA['id'], 
                            "name": self.PROJECT_DATA['name'] },
                            'code': "{}".format(self.sequence_number),
                'description': '',
                'sg_status_list': 'wtg'
            }

            creating_sequence = self.sg.create("Sequence", sequence_data)
            print( "Creating Sequence {} for Project: {}\nShotgrid Data: {}".format(self.sequence_number, self.PROJECT_DATA['name'], creating_sequence) )

    def create_new_shot(self, sequence_number=None, shot_number=None):
        '''
            Creates a shot inside a given Sequence, There is an expect that prevents the same shot from being made

            Args:
                sequence_number:            A string that will be the sequence number eg: "0010", "0020" ect
                shot_number:                A String that will be the shot inside the sequence eg: "0010_010" or "0020_010" ect
        '''


        shot = self.get_shot_info(shot_number=shot_number)

        if not shot[0]:
            seqeunce_number_data = self.get_sequence_info(sequence_number=sequence_number)

            self.sequence_id = None
            for seq_data in seqeunce_number_data:
                self.sequence_id = seq_data['id']

            shot_number = "{}".format(shot_number)

            data = {
                "project": {"type": "Project", 
                            "id": self.PROJECT_DATA['id'],
                            'name':self.PROJECT_DATA['name']},
                "sg_sequence": {"type": "Sequence", "id": self.sequence_id},
                "code": shot_number,
                'sg_status_list': "wtg",
                "task_template": {"type": "TaskTemplate", "id": self.GLOBAL_SHOT_TASK_TEMPLATE}
            }
            self.sg.create('Shot', data)
            print("New Shot has been created. Shot Number: {}, Sequence Number: {}".format(shot_number, sequence_number))
        else:
            message = "Shot {} already exist you can't create the same shot".format( shot_number )
            print(message)
            return False

    def create_new_asset(self, asset_type, asset_name):
        '''
            Creates a new asset entity on Shotgrid 

            Args:
                asset_type:                 This refers to the what kind of asset is it, a Character, Prop, Set ect
                asset_name:                 The actual name of the assets
        '''

        asset_data = {"project": {"type": "Project", "id": self.PROJECT_DATA['id']},
                    'code': asset_name,
                    "sg_asset_type": asset_type,
                    "sg_status_list": 'wtg',
                    'task_template': {"type":"TaskTemplate", 'id': self.GLOBAL_ASSET_TASK_TEMPLATE}}
        
        asset = self.sg.create("Asset", asset_data)
        print(asset)

    def create_new_version(self, 
                           shot_number=None, 
                           task='', 
                           asset_name=None, 
                           version_name=None, 
                           notes=None, 
                           path_to_frames=None, 
                           username='', 
                           file='', 
                           focal_length=None, 
                           cut_in=None,
                           cut_out=None, 
                           tags=None, 
                           department=None,
                           movie_path=None):
        
        '''
            Creates a new version entity on Shotgrid and uploades a file to a specific Shot and to a specific Task

            Args:
                shot_number                         The number of the shot you uploading to
                task                                The task that the upload is for, comp_qc, light, set extension ect
                asset_name                          The name of the asset you are uploading
                version_name                        This name of the scene file version   
                notes                               Any notes that will be uploaded with the file
                path_to_frames                      A path to frames 
                movie_path                          The Path to the quicktime mov
                username                            The user that is doing the uploading, this name must be the name as it appears on Shotgrid
                file                                The path of the mov file you are uplading
                department                          The department you wanting to publish to
                tags                                Who ever you want to tag, this needs to be a LIST
        '''
        task_info = self.get_task_info(shot_number=shot_number, task=task, asset_name=asset_name)
        shot_info = self.get_shot_info(shot_number=shot_number)
        asset_info = self.get_asset_info(asset_name=asset_name)
        user_info = self.get_user_info(username=username)



        for s_info in shot_info:
            self.shot_id = s_info['id']

        for u_info in user_info:
            self.user_id = u_info['id']

        for a_info in asset_info:
            self.asset_id = a_info['id']

        shot_or_asset_entity = []
        if asset_name:
            shot_or_asset_entity.append( {"type": "Asset", "id": self.asset_id })
        elif shot_number:
            shot_or_asset_entity.append( {"type": "Shot", "id": self.shot_id })


        ## Getting the tags
        self.tags = None
        if tags:
            self.tags = tags


        self.movie_path = None
        if movie_path:
            self.movie_path = movie_path

            



        version_data = {
            "project" : {"type": "Project", "id": self.PROJECT_DATA['id']},
            "description": notes,
            'sg_path_to_frames': path_to_frames,
            "sg_status_list": 'rev',
            "sg_path_to_movie": movie_path,
            "sg_department": department,
            'sg_task': {"type": "Task", "id": task_info['id']},
            "user": {'type': "HumanUser", "id": self.user_id},
            "entity": shot_or_asset_entity[0],
            "code": version_name,
        }


        version = self.sg.create('Version',  version_data)

        ## Upload the media to the given version
        self.sg.upload("Version", version['id'], 
                path=file, 
                field_name="sg_uploaded_movie",
                tag_list=self.tags)


        ## This updates the shot information, Does Not upload anything
        self.update_shot(shot_number=shot_number, 
                        task=task, 
                        task_status='rev', 
                        focal_length=focal_length, 
                        cut_in=cut_in, 
                        cut_out=cut_out)

        return version
    


    ######################################################################################################

    ###### ---------            get_Functions: Get functions                                --------######

    ### These Functions Deal with Reading or Getting information about anything on Shotgrid

    ######################################################################################################


    def get_shot_info(self, shot_number):
        '''
            Gets all the information related to a shot
            Args:
                shot_number:            The full shot number eg 010_0010
        '''
        filters = [["code", "is", shot_number]]
 
        shot_info = self.sg.find("Shot", filters, self.ADDITIONAL_SHOT_FILTERS)

        return shot_info
    
    def get_sequence_info(self, sequence_number):
        '''
            Gets the information of a sequence number

            Args:
                sequence_number:            The Sequence number as it appears on Shotgrid 
            
            Returns:
                dict:
                    - sequence id
                    - all the shots in the sequence 
        '''
        filters = [['code', 'is', sequence_number]]

        sequence_data = self.sg.find("Sequence", filters, self.ADDITIONAL_SEQUENCE_FILTERS)

        return sequence_data
    
    def get_asset_info(self, asset_name):
        '''
            Gets the information of a given Asset

            Args:
                asset_name:         asset name as a string
        '''
        filters = [['code', 'is', asset_name]]
        asset_info = self.sg.find('Asset', filters, self.ADDITIONAL_ASSET_FILTERS)

        return asset_info

    def get_task_info(self, shot_number=None, task='', asset_name=None):
        '''
            Gets all the information related to a Task for a given shot
            information like Pipeline Step or task status ect

            Args:
                shot_number (str)                 The number of a given shot
                task (str)                        The name of the task
        '''

        if not asset_name == None:
            if shot_number:
                return "You can't add [ Asset Name ] and [ Shot number ] both as a argument, only One can be provide."
            else:
                asset_info = self.get_asset_info(asset_name=asset_name)

                for info in asset_info:
                    asset_id = info['id']

                    filters = [["entity", "is", {"type": "Asset", "id": asset_id}],
                            ["content", 'is', task]]
                    task_info = self.sg.find_one("Task", filters, self.ADDITIONAL_TASK_FILTERS)
                    return task_info
            
        if not shot_number == None:
            shot_info = self.get_shot_info(shot_number=shot_number)

            for info in shot_info:
                shot_id = info['id']

                filters = [["entity", "is", {"type": "Shot", "id": shot_id}],
                        ["content", 'is', task]]
                task_info = self.sg.find_one("Task", filters, self.ADDITIONAL_TASK_FILTERS)
                return task_info
            
        if shot_number == None:
            if asset_name == None:
                return "You need to provide either a Shot number or Asset Name as a argument"

    def get_all_tasks(self, shot_number=None, asset_name=None):
        '''
            Returns all the tasks for a given shot or asset
        '''
        shot_info = self.get_shot_info(shot_number=shot_number)
        asset_info = self.get_asset_info(asset_name=asset_name)

        if shot_number:
            for tasks in shot_info:
                all_tasks = tasks['tasks']
                return all_tasks
        elif asset_name:
            for tasks in asset_info:
                all_tasks = tasks['tasks']
                return all_tasks
        else:
            raise ValueError("A [ shot_number ] or [ asset_name ] argument is needed")
            
    def get_user_info(self, username):
        '''
            Gets and Returns information regarding the user like Assigned Project, Permissions ect

            Args:
                username:           The user name as it appears on shotgrid but also can accept email address as a login
        '''
        try:
            if username.endswith(".com"):
                filters = [["email", "is", username]]
                people = self.sg.find("HumanUser", filters, self.ADDITIONAL_USER_FILTERS)
                return people
            else:
                filters = [["name",'is', username]]
                people = self.sg.find("HumanUser", filters, self.ADDITIONAL_USER_FILTERS)
                return people
        except:
            return traceback.format_exc()

    def get_version_info(self, version_name=None):
        '''
            Gets the information for a given version

            Arg:
                version_name:                   The name of the version as it appears on Shotgrid
        '''
        filters = [["code", "is", version_name]]
 
        shot_info = self.sg.find("Version", filters, self.ADDITIONAL_VERSION_FILTERS)

        return shot_info

    def get_all_tags(self):
        '''
            Gets and Returns all the tags that were created from the Tags page

            Returns;
                ID
                Name
        '''
        data = [["usage", "greater_than", -1]]
       

        tags = self.sg.find("Tag", data, self.ADDITIONAL_TAG_FILTERS)
        return tags

    def get_all_active_users(self):
        '''
            Gets and Returns all the User that have there status as Active
            Returns as a standard Shogrid Dict:
                ID
                Permissions
                Projects

        '''
        data = [["sg_status_list", "is", "act"]]

        all_users = self.sg.find("HumanUser", data, self.ADDITIONAL_USER_FILTERS)
        return all_users
    
    def get_all_sequences(self):
        '''
            Gets all the Sequences for a given Project along with the shots inside that sequence
        '''
        fields = ['code', 'shots']
        filters = [["project", "is", {'type': "Project", "id": self.PROJECT_DATA['id'] }]]

        sequence_data = self.sg.find("Sequence", filters, fields)

        return sequence_data
    
    def get_all_asset_categories(self):
        '''
            Gets all the Assets Categories from a given project
            Returns a dic of:
                asset catogory
                id
                type
        '''
        fields = ['sg_asset_type']
        filters = [["project", "is", {'type': "Project", "id": self.PROJECT_DATA['id'] }]]

        asset_category = self.sg.find("Asset", filters, fields)

        return asset_category
    
    def get_all_assets_from_a_category(self, asset_category):
        '''
            Gets all the Assets from a given asset Category for a given project
            Returns a dic of:
                asset name
                id
                type
        '''
        fields = ['code']
        filters = [["project", "is", {'type': "Project", "id": self.PROJECT_DATA['id'] }], ['sg_asset_type', 'is', str(asset_category)]]

        asset_data = self.sg.find("Asset", filters, fields)

        return asset_data

    def get_project_info(self):
        '''
            Gets information about a given project, only if the project has active statuss
        '''
 

        filters = [["id", "is" , self.PROJECT_DATA['id'] ]]

        shot_info = self.sg.find("Project", filters, self.ADDITIONAL_PROJECT_FILTERS)
        return shot_info

    ######################################################################################################

    ###### ---------            update_Functions: Update functions                          --------######

    ### These Functions Deal with Update an Entity weather a shot/asset or sequence on Shotgrid

    ######################################################################################################


    def update_shot(self, shot_number="", focal_length=None, cut_in=None, cut_out=None, task=None, task_status=None):
        '''
            Update the Shot entity, This is not [ Version info ] , it is Shot Info Tab
            If None is given for the option arguments then it uses the current value that already exists on Shotgrid 

            Args:
                shot_number (str)               The number of the shot as a string

            Optional Args:
                focal_length (float)            The focal length number as a float value
                cut_in (str)                    The start value of the shot as a string
                cut_out (str)                   The end value of the shot as a string
                task (str)                      The task of a shot eg comp or light or animation ect
                task_status (str)               The status of a task
        '''

        shot_info = self.get_shot_info(shot_number=shot_number)


        for info in shot_info:
            
            ## This checks if the focal length fields was enter or not
            ## If the field has no fields it will use what was already present in the fields
            focal_length_info = []
            if focal_length == None:
                focal_length_info.append( info['sg_focal_length'] )
            else:
                focal_length_info.append( focal_length )

            ###############################################################################
            ## Updating the Cut in information
            cut_in_info = []
            if cut_in == None:
                cut_in_info.append( info['sg_cut_in'] )
            else:
                cut_in_info.append( cut_in )

            ###############################################################################
            ## Updating the Cut Out information
            cut_out_info = []
            if cut_out == None:
                cut_out_info.append( info['sg_cut_out'] )
            else:
                cut_out_info.append( cut_out )

            ###############################################################################
            ## Updating the Cut Duration
            cut_duration = int(cut_out_info[0]) - int(cut_in_info[0])


            data = {
                "sg_focal_length": focal_length_info[0],
                "sg_cut_in": cut_in_info[0],
                "sg_cut_out": cut_out_info[0],
                "sg_cut_duration": cut_duration
                
            }
            update_info = self.sg.update("Shot", info['id'], data)

            #####################################################################################
            #####################################################################################
            ## This Handles everything task related like change the task status ect
            if not task == None:
                task_info = self.get_task_info(shot_number=shot_number, task=task)

                data = {
                    "sg_status_list": task_status
                }
                
                task_info = self.sg.update("Task", task_info['id'], data)
                return update_info, task_info

    def update_asset(self, asset_name, task=None, task_status=None):
        '''
            Updates the Asset Entity for any given asset

            Args:
                asset_name (str)                The name of the asset as it appears on Shotgrid

            Optional Args:
                task (str)                      The type of task as it appears on Shotgrid
                task_status (str)               The status you want to set the task to
        '''

        asset_info = self.get_asset_info(asset_name=asset_name)

        


        if not task == None:
            asset_task_info = self.get_task_info(asset_name=asset_name, task=task)

            ## If no task status is given as a argument, the current task status will be used
            task_status_info = []
            if task_status == None:
                task_status_info.append( asset_task_info['sg_status_list'] )
            else:
                task_status_info.append(task_status)


            data = {
                "sg_status_list": task_status_info[0]
            }

            self.sg.update("Task", asset_task_info['id'], data)
            return asset_info





