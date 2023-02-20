from setuptools import setup

setup(
    name='pypgpeed',
    version='0.1.2',
    packages=['pypgpeed'],
    entry_points = {
        'console_scripts': ['pypgpeed=pypgpeed.run:run'],
    },
    install_requires=["PyQt6", "PGPy", "qt_material", "pyperclip"],
    url='https://github.com/lewis-morris/pypgped',
    license='mit',
    author='Lewis Morris',
    author_email='lewis.morris@gmail.com',
    description='Python local PGP tool'
)
