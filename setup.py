from setuptools import setup, find_packages
import os

# 读取README
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

setup(
    name="crop-model-multi-stages",
    version="1.0.0",
    author="Wei Yifan",
    author_email="silence.63@163.com",
    description="基于生理过程的多物候期作物生长模拟模型",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/Weiyifan/Crop_Model_Multi_Stages",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Agriculture",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.18.0",
        "pandas>=1.0.0",
        "matplotlib>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    keywords="crop model, agriculture, simulation, phenology, yield prediction, multi-stage",
    project_urls={
        "Bug Reports": "https://github.com/Weiyifan/Crop_Model_Multi_Stages/issues",
        "Source": "https://github.com/Weiyifan/Crop_Model_Multi_Stages",
    },
)
