from setuptools import setup, find_packages

setup(
    name='cygen',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        "clang",
        "tree-sitter",
        "tree-sitter-cpp",
    ],
    entry_points={
        'console_scripts': [
            'cygen=cygen.cygen:main',  # Replace with your module and function
        ],
    },
)

