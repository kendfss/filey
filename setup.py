from setuptools import setup, find_packages

with open('README.md', 'r') as fob:
    long_description = fob.read()

setup(
    name='filey',
    version='0.0.2',
    author='Kenneth Sabalo',
    author_email='kennethsantanasablo@gmail.com',
    url='https://tildegit.org/eli2and40/filey',
    packages=['filey'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='utilities operating path file system',
    license='MIT',
    requires=[
        "audio_metadata",
        "dill",
        "filetype",
        "send2trash",
        "sl4ng",
        "pypeclip",
    ],
    python_requires='>3.9',
)