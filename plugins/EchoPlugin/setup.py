from setuptools import setup, find_packages

setup(
    name="echo_plugin",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'fastapi',
    ],
    entry_points={
        'my_fastapi_app.plugins': [
            'echo_plugin = EchoPlugin.routes:add_routes',
        ],
    }
)
