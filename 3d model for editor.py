import bpy
import threading
from bpy.props import StringProperty, PointerProperty, IntProperty, CollectionProperty
import time
import requests

# Define Property Group for Iterations
class IterationItem(bpy.types.PropertyGroup):
    iteration: IntProperty(name="Iteration")
    source: StringProperty(name="Source")

# Define Property Group for Model Generator Properties
class ModelGeneratorProperties(bpy.types.PropertyGroup):
    api_key_1: StringProperty(name="API Key 1")
    api_key_2: StringProperty(name="API Key 2")
    api_key_3: StringProperty(name="API Key 3")
    api_key_4: StringProperty(name="API Key 4")
    prompt: StringProperty(name="Prompt")
    status: StringProperty(name="Status", default="")
    iterations: CollectionProperty(type=IterationItem)

# Define Panel for 3D Model Generator
class OBJECT_PT_model_generator(bpy.types.Panel):
    bl_label = "3D Model Generator"
    bl_idname = "OBJECT_PT_model_generator"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Ensure model_generator_props is initialized
        if not hasattr(scene, "model_generator_props"):
            return

        model_gen_props = scene.model_generator_props

        # Draw Iteration Window
        row = layout.row()
        row.label(text="Iterations")
        box = layout.box()
        for iteration in model_gen_props.iterations:
            row = box.row()
            row.label(text=f"Iteration: {iteration.iteration}, Source: {iteration.source}")

        layout.prop(model_gen_props, "prompt")

        layout.prop(model_gen_props, "api_key_1")
        layout.prop(model_gen_props, "api_key_2")
        layout.prop(model_gen_props, "api_key_3")
        layout.prop(model_gen_props, "api_key_4")
        
        row = layout.row()
        row.scale_y = 1.0
        row.operator("object.generate_models", text=model_gen_props.status or "Generate", icon='PLAY')

        if model_gen_props.status == "Generating...":
            row = layout.row()
            row.label(text="Generating...", icon='TIME')
            self.animate_generate_button(row)

    def animate_generate_button(self, row):
        frame_current = int(time.time() * 2) % 8
        icons = ['NONE', 'KEYFRAME', 'TIME', 'AUTO', 'RESTRICT_VIEW_ON']
        icon = icons[frame_current % len(icons)]
        row.label(icon=icon)

# Define Operator to Generate Models
class OBJECT_OT_generate_models(bpy.types.Operator):
    bl_idname = "object.generate_models"
    bl_label = "Generate Models"

    @classmethod
    def poll(cls, context):
        return context.scene.model_generator_props.status == ""

    def execute(self, context):
        props = context.scene.model_generator_props
        
        if not props.prompt:
            self.report({'ERROR'}, "Please input prompt!")
            return {'CANCELLED'}
        
        props.status = "Generating..."
        threading.Thread(target=self.generate_models, args=(context,)).start()
        return {'RUNNING_MODAL'}

    def reset_status(self, context):
        context.scene.model_generator_props.status = ""

    def generate_models(self, context):
        props = context.scene.model_generator_props
        prompt = props.prompt
        api_keys = [props.api_key_1, props.api_key_2, props.api_key_3, props.api_key_4]

        models = []
        models.append(self.call_api_1(api_keys[0], prompt))
        models.append(self.call_api_1(api_keys[0], prompt))  # Call API 1 a second time
        
        bpy.app.invoke(self.models_generated, models)

    def call_api_1(self, api_key, prompt):
        url = "https://api.meshy.ai/v1/text-to-texture"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        data = {"prompt": prompt}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def models_generated(self, context, models):
        props = context.scene.model_generator_props
        props.status = ""

        # Clear previous iterations
        props.iterations.clear()

        # Add new iterations to the property group
        for idx, model in enumerate(models):
            iteration = props.iterations.add()
            iteration.iteration = idx + 1
            iteration.source = f"API {idx // 2 + 1} - Model {idx % 2 + 1}"

        # Add code to handle the generated models
        print(models)

# Register classes and properties
def register():
    bpy.utils.register_class(IterationItem)
    bpy.utils.register_class(ModelGeneratorProperties)
    bpy.types.Scene.model_generator_props = PointerProperty(type=ModelGeneratorProperties)
    bpy.utils.register_class(OBJECT_PT_model_generator)
    bpy.utils.register_class(OBJECT_OT_generate_models)

def unregister():
    bpy.utils.unregister_class(IterationItem)
    bpy.utils.unregister_class(ModelGeneratorProperties)
    del bpy.types.Scene.model_generator_props
    bpy.utils.unregister_class(OBJECT_PT_model_generator)
    bpy.utils.unregister_class(OBJECT_OT_generate_models)

# If running as standalone script, register the addon
if __name__ == "__main__":
    register()
