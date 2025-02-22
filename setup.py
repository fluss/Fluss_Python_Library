from setuptools import setup, find_packages

setup(
    name="fluss_api",
    version="0.1.9.9",
    packages= find_packages(),
    install_requires =[

    ],
    author="Marcello Jardim",
    author_email="marcello@fluss.io",
    description='A library to integrate the Fluss API into Home Assistant',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)