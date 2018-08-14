from setuptools import setup, find_packages
setup(name='pulse',
      version='1.0',
      packages=find_packages(include="pulsignal.*"),
      entry_points={
            "console_scripts": [
                  "pulsignal = pulsignal.main:main"
            ]
      }
      )