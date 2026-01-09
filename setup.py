from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="cashflow",
    version="1.0.0",
    description="Cashflow Desktop Application",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'cashflow=cashflow.__main__:main',
        ],
    },
    python_requires='>=3.8',
)
