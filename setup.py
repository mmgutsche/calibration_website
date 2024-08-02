from setuptools import setup, find_packages

setup(
    name="calibration_website",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-dotenv",
        "sqlalchemy",
        "aiofiles",
        "jinja2",
        "httpx",
        "pytest",
        "pytest-asyncio",
    ],
    entry_points={
        "console_scripts": [
            # If you have any command line scripts
            # 'script_name = module:function',
        ],
    },
    package_data={
        "": ["static/*", "templates/*", "questions.json"],
    },
)
