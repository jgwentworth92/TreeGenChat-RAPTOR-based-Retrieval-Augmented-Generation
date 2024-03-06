from setuptools import setup, find_packages

setup(
    name="hello_plugin",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'fastapi',
    ],
    entry_points={
        'my_fastapi_app.plugins': [
            'hello_plugin = hello_plugin.routes:add_routes',
        ],
    }
)
