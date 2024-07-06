import bpy
import threading
from bpy.props import StringProperty, PointerProperty, IntProperty, CollectionProperty
import time
import requests
import os

class IterationItem(bpy.types.PropertyGroup):
    iteration: IntProperty(name="Iteration")
    source: StringProperty(name="Source")

class ModelGeneratorProperties(bpy.types.PropertyGroup):
    api_key_1: StringProperty(name="API Key 1")
    api_key_2: StringProperty(name="API Key 2")
    api_key_3: StringProperty(name="API Key 3")
    api_key_4: StringProperty(name="API Key 4")
    prompt: StringProperty(name="Prompt")
    status: StringProperty(name="Status", default="")
    iterations: CollectionProperty(type=IterationItem)

class OBJECT_PT_model_generator(bpy.types.Panel):
    bl_label = "3D Model Generator"
    bl_idname = "OBJECT_PT_model_generator"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
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

        # Update button text based on status
        if model_gen_props.status == "Generating...":
            row.operator("object.generate_models", text="Generating...", icon='TIME')
        elif model_gen_props.status == "Completed":
            row.operator("object.generate_models", text="Completed", icon='CHECKMARK')
        else:
            row.operator("object.generate_models", text="Generate", icon='PLAY')

class OBJECT_OT_generate_models(bpy.types.Operator):
    bl_idname = "object.generate_models"
    bl_label = "Generate Models"

    @classmethod
    def poll(cls, context):
        return context.scene.model_generator_props.status in ("", "Completed", "Failed")

    def execute(self, context):
        props = context.scene.model_generator_props
        
        if not props.prompt:
            self.report({'ERROR'}, "Please input prompt!")
            return {'CANCELLED'}
        
        props.status = "Generating..."
        threading.Thread(target=self.generate_models, args=(context,)).start()
        return {'RUNNING_MODAL'}

    def generate_models(self, context):
        props = context.scene.model_generator_props
        prompt = props.prompt
        api_keys = [props.api_key_1, props.api_key_2, props.api_key_3, props.api_key_4]

        models = []
        success = True

        # Call the API twice as per your logic
        result_1 = self.call_api(api_keys[0], prompt)
        result_2 = self.call_api(api_keys[0], prompt)

        if result_1 is not None:
            models.append(result_1)
        else:
            success = False

        if result_2 is not None:
            models.append(result_2)
        else:
            success = False

        bpy.app.timers.register(lambda: self.models_generated(context, models, success))

    def call_api(self, api_key, prompt):
        url = "https://api.meshy.ai/v2/text-to-3d"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "mode": "preview",
            "prompt": prompt,
            "art_style": "realistic",
            "negative_prompt": "low quality, low resolution, low poly, attractive"
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            task_id = response.json().get('result')
            if not task_id:
                raise ValueError("No task ID returned in response")
            
            time.sleep(5)
            
            while True:
                response = requests.get(f"https://api.meshy.ai/v1/text-to-texture/{task_id}", headers=headers)
                response.raise_for_status()
                result = response.json()
                        
                if result['status'] == 'SUCCEEDED':
                    return result
                elif result['status'] == 'FAILED':
                    return None
                else:
                    time.sleep(10)

        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        return None

    def download_model(self, model_url, filename):
        """Download the model file from the provided URL and save it to the given filename."""
        try:
            response = requests.get(model_url)
            response.raise_for_status()
            with open(filename, 'wb') as file:
                file.write(response.content)
            return filename
        except Exception as e:
            print(f"Failed to download model: {e}")
            return None

    def import_model(self, filepath):
        """Import the model into Blender based on the file extension."""
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".obj":
            bpy.ops.import_scene.obj(filepath=filepath)
        elif ext == ".fbx":
            bpy.ops.import_scene.fbx(filepath=filepath)
        # Add more import options as needed
        else:
            print(f"Unsupported file format: {ext}")

    def models_generated(self, context, models, success):
        """Handle the generated models by downloading and importing them into Blender."""
        props = context.scene.model_generator_props
        props.status = "Completed" if success else "Failed"

        props.iterations.clear()

        for idx, model in enumerate(models):
            iteration = props.iterations.add()
            iteration.iteration = idx + 1
            iteration.source = f"API {idx // 2 + 1} - Model {idx % 2 + 1}"
            
            if model:
                model_url = model['download_url']  # Adjust based on actual API response
                # Save models in the current .blend file directory
                filename = os.path.join(bpy.path.abspath("//"), f"model_{idx+1}.obj")
                filepath = self.download_model(model_url, filename)
                if filepath:
                    self.import_model(filepath)

        print(models)
        return None

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

if __name__ == "__main__":
    register()
