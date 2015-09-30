from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='gearmanny',
      version='0.1',
      description='A simplified Gearman wrapper',
      #url='http://github.com/storborg/funniest',
      author='Terrasque',
      long_description=readme(),
      author_email='terrasque@thelazy.net',
      #license='MIT',
      packages=[
            'gearmanny',
            "gearmanny.helpers",
        ],
      install_requires=[
          'gearman',
      ],
      include_package_data=True,
      zip_safe=False)