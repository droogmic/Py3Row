from setuptools import setup, find_packages

setup(
    name="pyrow",
    version="0.1",
    packages=find_packages(exclude=["csafe"]),
    # scripts=['examples/statshow.py', 'examples/strokelog.py'],

    install_requires=['pyusb==1.0'],
    python_requires='>=3.5',

    package_data={
    },

    # metadata for upload to PyPI
    author="Michael Droogleever",
    author_email="droogmic@yahoo.com",
    description="Concept2 indoor rowing maachine interface",
    license="BSD-2",
    keywords="rowing concept2",
    # url="http://example.com/HelloWorld/",   # project home page, if any
    # could also include long_description, download_url, classifiers, etc.
)
