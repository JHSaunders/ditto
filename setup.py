from setuptools import setup, find_packages
setup(
    name= "ditto",
    version = 0.1,
    packages=find_packages(),
    
    entry_points="""
        [console_scripts]
        ditto = ditto.core:main
    """
)
