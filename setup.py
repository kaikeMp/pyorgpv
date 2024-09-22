from setuptools import setup, find_packages

setup(
    name='pypv',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'scipy',
        'matplotlib',
    ],
    author='Kaike Pacheco',
    author_email='fisikaike@live.com',
    description='Biblioteca para análise de curvas IV de células solares',
    url='https://github.com/seu_usuario/pypv',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
