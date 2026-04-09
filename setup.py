from setuptools import setup, find_packages

setup(
    name="chronolight",
    version="1.6.1",
    author="Sviter",
    description="A simple library for easily working with time",
    url="https://github.com/ISviterI/chronolight",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    project_urls={
        "Homepage": "https://github.com/ISviterI/chronolight",
        "Discord": "https://discord.gg/MXv3KTFmPE",
        "Wiki": "https://github.com/ISviterI/chronolight/wiki",
        "Documentation": "https://github.com/ISviterI/chronolight/wiki/Documentation",
    },
    packages=find_packages(),
    license="MIT",
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="chronolight,chrono,timelines,delay,time,timeline,after,after_delay,afterdelay,light,chronos,simple,easy,easytoworkwith,easy_to_work_with,very_simple,cool,peak,bruh,lol,chains,chain,class,working_with_time",
)