# Tool for mtsblend (mitsuba for blender)
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENSE BLOCK *****

import bpy
import mathutils

def get_worldscale( as_scalematrix=True):
    ws = 1

    scn_us = bpy.context.scene.unit_settings

    if scn_us.system in {'METRIC', 'IMPERIAL'}:
        # The units used in modelling are for display only. behind
        # the scenes everything is in meters
        ws = scn_us.scale_length

    if as_scalematrix:
        return mathutils.Matrix.Scale(ws, 4)

    else:
        return ws


def lookAt(matrix):
    '''
    Derive a list describing 3 points for a Mitsuba LookAt statement

    Returns     3 tuple(3) (floats)
    '''

    ws = get_worldscale()
    matrix *= ws
    ws = get_worldscale(as_scalematrix=False)
    matrix[0][3] *= ws
    matrix[1][3] *= ws
    matrix[2][3] *= ws
    # transpose to extract columns
    matrix = matrix.transposed()
    pos = matrix[3]
    forwards = -matrix[2]
    target = (pos + forwards)
    up = matrix[1]

    return (pos, target, up)



class OP_Gen_lookat_params(bpy.types.Operator):
    bl_idname = "gdco.gen_cam_lookat_params"
    bl_label = "Export cameras lookat params"
    bl_description = "Generate lookat parameters from cameras"

    export_group = bpy.props.StringProperty(name="GroupName", default="cam_to_export")
    export_file  = bpy.props.StringProperty(name="Lookat Filepath", default="//cameras.lookat", subtype='FILE_PATH')

    def __init__(self):
        self.grp = bpy.data.groups[0] if bpy.data.groups[0] else None

    @classmethod
    def poll(self, ctx):
        return True

    def execute(self, ctx):
        if self.export_group in bpy.data.groups:
            print('save params at',bpy.path.abspath(self.export_file))
            f = open(bpy.path.abspath(self.export_file),'w')
            for cam in bpy.data.groups[self.export_group].objects:
                o,t,u = lookAt(cam.matrix_world)
                name = cam.name
                f.write( '{} -D origin={},{},{} -D target={},{},{} -D up={},{},{}\n'.format( name,o[0],o[2],-o[1],t[0],t[2],-t[1],u[0],u[2],-u[1]) )
            f.close()
        else:
            print(self.export_group,": group not found")

        return {'FINISHED'}


class LookatParamPanel(bpy.types.Panel):
    bl_label = 'Lookat Params'
    bl_space_type = 'PROPERTIES'
    bl_region_type= 'WINDOW'
    bl_context = 'scene'

    def draw(self, ctx):
        layout = self.layout
        row = layout.row()
        op_prop = row.operator(OP_Gen_lookat_params.bl_idname)



def register():
    bpy.utils.register_class(gen_lookat_param_Settings)
    bpy.utils.register_class(LookatParamPanel)
    bpy.utils.register_class(OP_Gen_lookat_params)

    bpy.types.Scene.gen_lookat_params=bpy.props.PointerProperty(type=gen_lookat_param_Settings)

def unregister():
    bpy.utils.register_class(gen_lookat_param_Settings)
    bpy.utils.register_class(LookatParamPanel)
    bpy.utils.register_class(OP_Gen_lookat_params)

    del bpy.types.Scene.gen_lookat_params

