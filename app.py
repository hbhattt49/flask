from setuptools import setup, find_packages

setup(
    name='one_time_token_extension',
    version='0.1',
    packages=find_packages(),
    install_requires=['jupyter_server'],
    entry_points={
        'jupyter_serverproxy_servers': []
    }
)
