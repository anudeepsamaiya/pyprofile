import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyprofile", # Replace with your own username
    version="0.0.1",
    author="Anudeep Samaiya",
    author_email="anudeepsamaiya@gmail.com",
    description="Python profiling and visualizing package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anudeepsamaiya/pyprofile",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
