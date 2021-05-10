from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='summaWorkflow_public',  # Required
    version='0.1',  # Required
    description='SUMMA workflow repository',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional
    url='https://github.com/CH-Earth/summaWorkflow_public',  # Optional
    author='Wouter Knoben',  # Optional
    author_email='Wouter.knoben@usask.ca',  # Optional
    keywords='hydrology, SUMMA',  # Optional

    # When your source code is in a subdirectory under the project root, e.g.
    # `src/`, it is necessary to specify the `package_dir` argument.
    package_dir={'': 'utility_scripts'},  # Optional
    packages=find_packages(where='utlity_scripts'),  # Required


    #python_requires='>=3.6, <4', # Optional
    #install_requires=requirements # Optional

)
