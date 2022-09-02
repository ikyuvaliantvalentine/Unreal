from PySide2 import *
import unreal, sys

class TestWidget(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super(TestWidget, self).__init__(parent)

		vbox = QtWidgets.QVBoxLayout(self)

		btn = QtWidgets.QPushButton("Auto Material Assignment")
		btn2 = QtWidgets.QPushButton("Create Cinem Cam")
		btn3 = QtWidgets.QPushButton("Delete Empty Folder")


		btn.clicked.connect(self.quick_assign_material)
		btn2.clicked.connect(self.btn_clicked_abc)
		btn3.clicked.connect(self.cleanup_empty_folder)

		vbox.addWidget(btn)
		vbox.addWidget(btn2)
		vbox.addWidget(btn3)

	def quick_assign_material(self):
		assets = unreal.EditorUtilityLibrary.get_selected_asset_data()
		try:
			asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
			project_mats =  asset_registry.get_assets(unreal.ARFilter(recursive_classes= True, class_names=["Material","MaterialInstance"]))
			for asset in assets:
				object_path = unreal.StructBase.get_editor_property(asset, 'object_path')
				package_name = str(unreal.StructBase.get_editor_property(asset, 'package_name'))
				package_path = unreal.StructBase.get_editor_property(asset, 'package_path')
				asset_name = str(unreal.StructBase.get_editor_property(asset, 'asset_name'))
				asset_class = unreal.StructBase.get_editor_property(asset, 'asset_class')
				if (asset_class == 'StaticMesh'):
					tmp_asset = unreal.load_asset(object_path)
					sm_component = unreal.StaticMeshComponent()
					sm_component.set_static_mesh(tmp_asset)
					mat_slot_names = unreal.StaticMeshComponent.get_material_slot_names(sm_component)
					for mat in mat_slot_names:
						for mats in project_mats:
							mats_name = unreal.StructBase.get_editor_property(mats, 'asset_name')
							if mats_name is mat:
								tmp_asset.set_material(tmp_asset.get_material_index(mat), mats.get_asset())
								unreal.EditorAssetLibrary.save_asset(object_path, True)
		except Exception as error:
			print(error)
	
	def btn_clicked_abc(self):
		#your lines to spawn the actor, i did use them as is, nothing changed
		actor_class = unreal.CineCameraActor
		actor_location = unreal.Vector(0.0,0.0,0.0)
		actor_rotation = unreal.Rotator(0.0,0.0,0.0)
		_spawnedActor = unreal.EditorLevelLibrary.spawn_actor_from_class(actor_class, actor_location, actor_rotation)

		#make the focus settings class, and set some values that we need
		_focusSettings = unreal.CameraFocusSettings()
		_focusSettings.manual_focus_distance = 1320.0
		_focusSettings.focus_method = unreal.CameraFocusMethod.MANUAL
		_focusSettings.focus_offset = 19.0
		_focusSettings.smooth_focus_changes = False

		#Apply the focus settings to the camera we made
		_cineCameraComponent = _spawnedActor.get_cine_camera_component()
		_cineCameraComponent.set_editor_property("focus_settings",_focusSettings)

	def cleanup_empty_folder(self):
		editor_asset_lib = unreal.EditorAssetLibrary()

		source_dir = "/Game/"
		include_subfolders = True
		deleted = 0

		assets = editor_asset_lib.list_assets(source_dir, recursive=include_subfolders, include_folder=True)
		folders = [asset for asset in assets if editor_asset_lib.does_directory_exist(asset)]

		for folder in folders:
			has_assets = editor_asset_lib.does_directory_have_assets(folder)

			if not has_assets:
				editor_asset_lib.delete_directory(folder)
				deleted += 1
				unreal.log("Folder {} without assets was deleted".format(folder))

		unreal.log("Deleted {} folders without assets".format(deleted))

		QMessageBox.information(self, "Info", "This is Information")

app = None
if not QtWidgets.QApplication.instance():
	app = QtWidgets.QApplication(sys.argv)	

widget = TestWidget()
widget.show()
unreal.parent_external_window_to_slate(widget.winId())