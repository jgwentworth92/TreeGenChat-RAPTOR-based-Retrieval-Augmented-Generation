import pkg_resources
from fastapi import FastAPI

def load_plugins(app: FastAPI):
    for entry_point in pkg_resources.iter_entry_points('my_fastapi_app.plugins'):
        try:
            plugin_add_routes = entry_point.load()
            plugin_add_routes(app)
            print(f"Loaded plugin: {entry_point.name}")
        except Exception as e:
            print(f"Failed to load plugin {entry_point.name}: {e}")
