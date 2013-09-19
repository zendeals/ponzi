import setuptools

import ponzi

setuptools.setup(
    name="ponzi",
    version=ponzi.version,
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'ponzi = ponzi.cli:main'
        ]
    },
    data_files=['lorem.txt', 'config.yaml', 'template.html', 'datasets/notredame.zip', 'datasets/stanford.zip'],
    install_requires=[x for x in open('requirements.txt').readlines()]
)
