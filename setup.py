from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="loki-middleware",
    version="0.1.0",
    description="Structured logging middleware for FastAPI with Loki integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="LEMBO Ilem Nelson",
    author_email="lemboilem@gmail.com",
    url="https://github.com/IlemLembo/loki-middleware",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
    ],
    python_requires=">=3.6",
    install_requires=[
        "fastapi>=0.136.0",
        "python-logging-loki>=0.3.1",
        "geocoder>=1.38.1",
        "dict_field_redacter>=0.1.3",
        "colorama>=0.4.6"
    ]
)