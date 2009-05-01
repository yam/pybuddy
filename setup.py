try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(name="PyBuddy",
      version="0.1",
      author='',
      author_email='',
      description="Python library to control your i-buddy",
      packages=find_packages(exclude=['ez_setup']),
      zip_safe=False
      )
