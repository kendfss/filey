from setuptools import setup, find_packages

with open('README.md', 'r') as fob:
    long_description = fob.read()

setup(
    name='filey',
    version='0.0.1',
    author='Kenneth Elisandro',
    author_email='eli2and40@tilde.club',
    url='https://tildegit.org/eli2and40/cabinet',
    # packages=find_packages(),
    packages=['filey'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='utilities productivity',
    license='MIT',
    requires=[
        'filetype',
        'audio_metadata',
        'send2trash',
        'sl4ng'
    ],
    # py_modules=['filey'],
    python_requires='>=3.8',

)