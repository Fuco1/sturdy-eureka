from setuptools import setup

setup(name='funniest',
      version='0.1',
      description='The funniest joke in the world',
      url='http://github.com/storborg/funniest',
      author='Flying Circus',
      author_email='flyingcircus@example.com',
      license='MIT',
      packages=['clod'],
      install_requires=[
          'ilio', 'vispy', 'numpy', 'PyOpenGL'
      ],
      zip_safe=False)
