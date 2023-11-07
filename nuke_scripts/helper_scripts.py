
'''

    These are a couple of Helpful scripts that can be used in NUKE

'''
import os
from PySide2 import QtWidgets
from PySide2 import QtCore as Core
from PySide2 import QtGui as Gui
from PySide2 import QtUiTools as Ui_Tools
import traceback





class Helper_Script():
    def __init__(self):
        pass


    def version_up_folder(self, path_to_versions):
        '''
            Gets the latest version folder and versions up or creates a new v001, able to get the version folder regardless of how its named, can be v1 or v0000002 should version up
            Args:
                path_to_versions:                       The full path to the directory when all the version folder live

            Returns:
                returns a dict containing the new version , eg if the latest version if v050 then it will return v051, if v999 it will return v1000
                if there is no version folder it will return v001

            NOTE: This function does NOT create a folder for you, you would still need to create one
        '''

        version_up_list = []
        version_path = path_to_versions.replace('\\','/')
        try:

            latest_version = []
            list_of_versions = os.listdir(version_path) ## The Latest version
            list_of_versions.sort()


            version_number_list = []
            ## This for loop is removing the 'v' and stripping away the leading '0' leaving the number left and appending it to the version number list
            ## eg: v010 becomes 10.....v005 becomes 5
            for i in list_of_versions:
                path = os.path.join( version_path, i)
                ignore_files = os.path.isfile(path) ## ignoring and files that might exist in the folder

                if not ignore_files:
                    if i.startswith('v'):
                        version_number = i.split('v')
                        ver_number = version_number[-1]
                        stripping_number = ver_number.lstrip('0')
                        version_number_list.append( stripping_number )


            sorted_list = sorted (version_number_list, key=int)
            latest_version_number = sorted_list[-1] ## Getting the last number in the list


            for version in list_of_versions:
                if version.endswith(latest_version_number):
                    latest_version.append( version )

            latest_matte_version = latest_version[0]
    
            version_number = latest_matte_version.split('v')[-1]
            versioned_up = int(version_number) + 1 ## increasing version number 
            
            version_length = len(str(versioned_up))
            padding_amount = 2/version_length ## Padding amount determines the amount of [ 0 ]'s  that will be needed 2 [v001], 1 [v01] or 0 [v1]
            
            
            padding = []
            for i in range(int(padding_amount)):
                padding.append('0')
                            
            amount_of_zeros = ''.join(padding)
            new_version_folder = "v{}{}".format(amount_of_zeros, versioned_up)
                            
            version_up_list.append( new_version_folder )
            print('version_up function debug -------- versioning up latest folder')

        except:
            print('version_up function debug -------- creating initial version one folder')

            ## The path given has no version folder so a v001 will be created
            new_version_folder = self.initial_version_folder_number
            version_up_list.append( new_version_folder )


        return_dict = {'new_version': version_up_list[0]}


        return return_dict
    



    def U_msg_pop_up(text, window_title=''):
            '''
                A small pop up window with a custom text, that overrides nukes popup message
                Args:
                    Text:               Display message when message pops up
                    window_title:       optional argument to add a title of the pop up window
                Returns:
                    Nothing
            '''
            width = 300
            heigh = int((width/2)*1.5)
            message = QtWidgets.QMessageBox()
            message.resize(width,heigh)
            message.windowTitle()
            message.setWindowFlags(Core.Qt.WindowStaysOnTopHint)
            message.setText( str(text) )
            if window_title:
                message.setWindowTitle( window_title )
            else:
                message.setWindowTitle("Warning")
            message.exec_()



    def get_sequences(self, path_to_version):
        '''
            Grabs and Returns some useful information which can be used for Read nodes when importing.
            Works with any path, given that the directory is the path where the image sequence or media file lives

            Argument:
                path_to_version:            this is the full string path that leads to the media file eg: = //nova/films2/tf_universal/shot_publish/0010/010/light/renders/rops/chr_02/v001


            Returns a dict:
                - full_path:                full path to be used on read nodes eg: '//nova/films2/tf_universal/shot_publish/0010/010/light/renders/rops/chr_01/v006/frame_%04d.exr'

                - first_frame:              first frame of the image sequence 

                - last_frame:               last frame of the image sequence

                - paddng_amount:            the padding amount from the file %04d = 4 frame padding, %08d = 8 ect

                - amount_of_frames:         the amount of frames in the folder 

                - missing_frames:           any missing frames in the sequence, returns them as a list [102-106, 108-112, 114-118, 120-124]

                - file_extension:           the file extension of the image sequence, eg '.exr', '.png' ect

                - frame_range:              the frames range '101-125'

                - colorspace:               rops: ACES - ACEScg ------- ( if these files are coming from lighting houdini ),
                                            nuke: ACES - ACES2065-1 ------- (if these are files that are coming out of nuke)
                                            srgb: Output - sRGB ----- (for layers that dont end in exr is png, jpegs ,mp4 , movs ect)

                - on_error:                 frame_error for setting read nodes to read the nearest frame
                                            this is need to be set if lighting renders step frames, if this isnt set it will error out on the inbetween frames

                - rops_layer_name           name of the rops layer, if there isnt one it would return as None

                - broken_frames             if there are any '_broken_frames' in the folder, returns them as a list [114, 142]


            NOTE: This currently doesn't read metadata from quicktime files like mov, mp4  ect, so certain fields listed below will read as None, when reading those file formats:
                first_frame
                last_frame
                amount_of_frames
                missing_frames
                frame_range
                broken_frames
        '''

        

 
        path_fix = path_to_version.replace('\\','/')

        try:
            msg = []
            render_dict = {} ## The dictionary that gets returned

            ## Fallback code incase the latest version doesnt have renders it will fallback to the most recent version that does
            current_version = []

            split_path = path_fix.split('/')
            del split_path[-1]
            rops_layer_path = '/'.join(split_path) ## example:  //nova/films2/stardust/shot_publish/0080/140/light/renders/rops/shad_01
    

            ## If the current version is empty it will fallback to the latest most recent version
            chosen_path = []

            print ('get_sequences debug......getting version')
            checking_for_files = os.listdir(path_fix)


            print ('checking_for_files: {}'.format(checking_for_files))
            if checking_for_files:
                chosen_path.append( path_fix )
            else:
                try:
                    msg.append(True)
                    items = [[]]
                    number_interate = 1
                    while not items[0]:
                        shot_versions = os.listdir(rops_layer_path)
                        shot_versions.sort()
                        
                        try:
                            latest_shot_path = os.path.join( rops_layer_path, shot_versions[-number_interate]).replace('\\','/')
                            exr_files = os.listdir(latest_shot_path)
                            #print (exr_files)
                            if exr_files:
                                fallback_version = shot_versions[- number_interate]
                                fallback_version_path_found = os.path.join( rops_layer_path, fallback_version)
                                chosen_path.append( fallback_version_path_found )
                                current_version.append( fallback_version )
                                
    
                                break
                            items.append( exr_files )
                            number_interate += 1

                        except:
                            files = os.listdir(path_fix)
                            error_msg = '\n{}\nPath given is empty. An Attempt was made to find a previous version that has renders but the search was unsuccessful. Double check that the given path has renders\nGiven Path: {}\nContents: {}'.format(traceback.format_exc(), path_fix, exr_files)
                            return error_msg
                except:
                    return traceback.format_exc()

            render_file_path = chosen_path[0].replace('\\','/') ## The path with the found version



            print ('get_sequences debug......getting rop_layer_name')
            ## Getting the name of the rops layer if path given is a rops layer, else None is returned
            layer_name = []
            file_split = render_file_path.split('/')
            rops_check = file_split[-3]
            if rops_check == 'rops':
                rop_layer_name = file_split[-2]
                layer_name.append(rop_layer_name)
            else:
                layer_name.append('None')


            ## Ignoring any renders with _broken_frames
            full_version_path = os.listdir( render_file_path )
            broken_frames_list = []
            frame_list = []
            seqs = pyseq.get_sequences(full_version_path) # Getting sequence information
            for items in seqs:
                if not items.startswith("_broken"):
                    frame_list.append(items)
                elif items.startswith('_broken'):
                    ## Getting the broken frames
                    broken_frames_list.append( items )



            print ('get_sequences debug......getting file size')
            ## Getting the file size in mb
            ## total file size( this is all the files in the folder added up )
            ## Getting per frame file size
            file_size_list = []
            per_frame_file_size = {}
            for files in full_version_path:
                if not files.startswith("_broken"): 
                    file_path = os.path.join( render_file_path, files)
                    file_size = os.stat(file_path).st_size/1000
                    file_size_list.append(file_size)
                    files = files.split('.')[0]
                    per_frame_file_size[files] = ('{0}{1}'.format(file_size,'.mb')) 

            total_file_size_in_mb = sum(file_size_list)/1000
            print ('get_sequences debug......getting file size complete: {}'.format( total_file_size_in_mb))


            print ('get_sequences debug......getting padding amount')
            # ## Getting the Frame padding amount
            # ## This is adaptive, which means if the padding count ever changes from 4 frame padding to something else, the padding count will automaically adjust
            frame_list.sort()
            extension = frame_list[-1].split('_')
            padding_amount = len(extension[-1].split('.')[-2]) # padding amount 


            sequence_to_import = frame_list[0]
            sequence_start_frame = int(sequence_to_import.format("%s")) # Start frame
            sequence_end_frame = int(sequence_to_import.format("%e")) # End Frame
            sequence_name = sequence_to_import.format("%h%p%t")
            new_sequence_name = sequence_name.replace("%d", "%0" + str(padding_amount) + "d")
            print ('get_sequences debug......getting padding amount complete: {}'.format(padding_amount))
            

            print ('get_sequences debug......getting start frame')
            # A contingency if renders layers are single frame renders
            # pyseq cant count the frames if its one frame it will return as 0
            # This checks if its one frame then
            # -- if a shot only has 1 frame on for example frame_101.exr, this will pull the frame number as its START and END frame
            frame_count = extension[-1].split('.')[0] ## the frame count before the file extension ie 0101 or 0105 ect
            start_frame = []
            if sequence_start_frame == 0:
                if frame_count.startswith('0'):
                    single_start_frame = frame_count.lstrip('0') ## stripping away the leading 0 in the frame number, 0101 becomes 101 ect
                    if not single_start_frame:
                        start_frame.append(0)
                    else:
                        start_frame.append(single_start_frame)
                else:
                    start_frame.append('None')
            else:
                start_frame.append(sequence_start_frame)
            print ('get_sequences debug......getting start frame complete: {}'.format(start_frame))

            print ('get_sequences debug......getting end frame')
            end_frame = []
            if sequence_end_frame == 0:
                if frame_count.startswith('0'):
                    single_end_frame = frame_count.lstrip('0') ## stripping away the leading 0 in the frame number
                    end_frame.append(single_end_frame)
                else:
                    end_frame.append('None')
            else:
                end_frame.append(sequence_end_frame)
            print ('get_sequences debug......getting end frame complete: {}'.format(end_frame))

            amount_of_frames = sequence_to_import.format('%l') ## Counts the files in the folder
            sequence_full_path = os.path.join( render_file_path, new_sequence_name).replace("\\","/") ## The full path that is returned


            ## This is used to set the read nodes in nuke depending where and what format it is
            ## If files are coming from houdini, like rops, you use the [ houdini ] key
            ## if something is rendered out from nuke and re-imported back in , use [ nuke ] key
            ## Any format NOT exr, formats like TIFF, JPEG, PNG , MP4, MOV ect , use [ srgb ] key
            ## Apply this on the colorspace knob for the read nodes
            colorspace = {'houdini': 'ACES - ACEScg', 'nuke': 'ACES - ACES2065-1', 'srgb': 'Output - sRGB'} 


            print ('get_sequences debug......getting frame range')
            ## Getting the list of frames if they exist, the frame range
            list_of_frame_ranges = []
            frame_range = sequence_to_import.format('%r')
            if frame_range:
                list_of_frame_ranges.append( frame_range )
            else:
                list_of_frame_ranges.append( "None" )
            print ('get_sequences debug......getting frame range complete: {}'.format(list_of_frame_ranges))


            print ('get_sequences debug......getting file extension')
            ## Getting file extensions 
            list_of_file_extensions = []
            file_extension = sequence_to_import.format('%t')
            if file_extension:
                list_of_file_extensions.append( file_extension )
            else:
                split_file = sequence_to_import.split('.')
                getting_file_type = split_file[-1]
   
                list_of_file_extensions.append(".{}".format(getting_file_type))
            print ('get_sequences debug......getting file extension complete!: {}'.format(list_of_file_extensions))



            print ('get_sequences debug......getting missing frames')
            ## Getting any missing frames
            list_of_missing_frames = []
            missing_frames = sequence_to_import.format('%M')
            if missing_frames:
                list_of_missing_frames.append(missing_frames)
            else:
                list_of_missing_frames.append('None')
            print ('get_sequences debug......getting missing frames complete: {}'.format(list_of_missing_frames))


            print ('get_sequences debug......getting list of broken frames')
            ## Getting any broken frames
            list_of_broken_frames = []
            try:
                broken_frames = broken_frames_list[0].format('%R')
                list_of_broken_frames.append( broken_frames )
            except IndexError:
                list_of_broken_frames.append('None')
            print ('get_sequences debug......getting list of broken frames complete!: {}'.format(list_of_broken_frames))



            print ('get_sequences debug......getting version')
            ## Getting Versions 
            ## This should get the version folder number regardless of where it sits in the directory path string
            ## example: '//nova/films2/tf_universal/shot_publish/0010/010/_reviewables/crowd/v001/renders/0001_arnold1/'...it will pick up v001 still
            ## another example: '//nova/films2/tf_universal/shot_publish/0010/010/_reviewables/edit/v033'... it will still pick up v033
            current_version_number = []
            try:
                if current_version:
                    current_version_number.append(current_version[0])

                else:
                    getting_version = path_fix.split('/')
                    version_sort = list(set(getting_version))
                    version_sort.sort()
                    version_number = version_sort[-1].split('v')[-1]
                    if version_number:
                        if version_sort[-1].startswith('v'):
                            current_version_number.append(version_sort[-1])
                        else:
                            current_version_number.append('None')
                    else:
                        current_version_number.append('None')

            except IndexError:
                current_version_number.append('None')
            print ('get_sequences debug......getting version complete!: {}'.format(current_version_number))

            print ('get_sequences debug......getting shot and sequence number')
            ## Getting the Shot and Sequence Number
            seq_split = sequence_full_path.split('/')
            current_sequence = []
            current_shot = []
            try:
                sequence_number = seq_split[6]
                shot_number = seq_split[7]
                if int(shot_number):
                    current_shot.append( shot_number )
                else:
                    current_shot.append( 'None' )

                if int(sequence_number):
                    current_sequence.append(sequence_number)

                else:
                    current_sequence.append( 'None' )
            except:
                pass
            print ('get_sequences debug......getting shot and sequence number complete!: Shot: {}, Sequence: {}'.format(current_shot, current_sequence))




            print ('get_sequences debug......creating dictionary')
            ## Creating the dictionary            
            render_dict['full_path'] = sequence_full_path # full rendeer path which can be used when adding the path to the read node
            render_dict['first_frame'] = start_frame[0] # start frame
            render_dict['last_frame'] = end_frame[0] # last frame
            render_dict['amount_of_frames'] = amount_of_frames # amount of frames in the folder
            render_dict['padding_amount'] = padding_amount # the padding count for the file
            render_dict['missing_frames'] = list_of_missing_frames[0]  # a list of missing frames
            render_dict['frame_range'] = list_of_frame_ranges[0] # frame range
            render_dict['file_extension'] = list_of_file_extensions[0] # file format
            render_dict['colorspace'] = colorspace # colorspace
            render_dict['on_error'] = 'nearest frame' # nearest_frame with gets set on Read nodes 
            render_dict['rops_layer_name'] = layer_name[0] # layer_name, option extra
            render_dict['broken_frames'] = list_of_broken_frames[0] # all the broken frames
            render_dict['total_file_size_in_mb'] = total_file_size_in_mb # total size of all files in directory
            render_dict['current_version'] = current_version_number[0] ## The latest version that has renders
            render_dict['current_sequence'] = current_sequence[0] ## The current sequence from the path string
            render_dict['current_shot'] = current_shot[0] ## The current shot from the path string
            #render_dict['per_frame_file_size'] = per_frame_file_size ## per frame file size


            print ('get_sequences debug......Complete!')
            print ('\n\n')
            if msg:
                folder_name = path_fix.split('/')[-2] ## name of the folder eg, bg_01 or chr_02 or edit ect
                version = path_fix.split('/')[-1]

                ## example: 0010_010 edit v033 is empty, falling back to most recent available version
                print ('{}_{} {} {} is empty, falling back to most recent available version'.format( current_sequence[0], current_shot[0], folder_name, version ))
            

            return render_dict

        except:
            return_message = "{}\nCant find renders from given file path, Path given might be empty, incorrect or contain broken frames.\n\nGiven Path: {}".format(  traceback.format_exc(),path_to_version)

            return return_message    
    
