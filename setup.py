from setuptools import setup, find_packages

setup(
   name='edbo',
   packages=['edbo'], 
   version='0.2.0',
   author='Jose A. Garrido Torres & Abigail Gutmann Doyle',
   author_email='josegarridotorres@me.com',
   url='https://github.com/doyle-lab-ucla/edboplus',
   keywords=['Bayesian Optimization', 'Chemical Reaction Optimization'],
   license='MIT',
   description='Bayesian reaction optimization as a tool for chemical synthesis.',
   install_requires=[
     'botorch==0.5.0',
     'gpytorch==1.5.1',
     'idaes-pse==1.5.1',
     'ipykernel==6.5.1',
     'ipython==7.29.0',
     'ipywidgets==7.6.5',
     'Jinja2==3.0.3',
     'joypy==0.2.6',
     'lxml==4.6.4',
     'mordred==1.2.0',
     'numpy==1.22.4',
     'ordered-set==4.0.2',
     'pandas==2.1.3',
     'pareto==1.1.1.post3',
     'pymoo==0.5.0',
     'scikit-learn==1.0.1',
     'scipy==1.7.2',
     'seaborn',
     'matplotlib',
     'sympy==1.9',
     'torch==1.10.0',
     'tqdm',
     'pydantic==1.8.2',
     'python-dotenv==0.19.0',
     'fastapi==0.104.1',
     'uvicorn==0.24.0',
     'python-multipart==0.0.6',
     'aiofiles==23.2.1',
     ],
   classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Science/Research', 
    'Topic :: Scientific/Engineering :: Chemistry',
    'License :: OSI Approved :: MIT License', 
    'Programming Language :: Python :: 3.8',
  ],
)
