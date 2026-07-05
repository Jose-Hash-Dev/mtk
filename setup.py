from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
	long_description = fh.read()

setup(
	name="mtk_property",
	version="1.0.0",
	description="MTK Property Management Module for Altensor",
	long_description=long_description,
	long_description_content_type="text/markdown",
	author="Yusif",
	author_email="yusif.hashimov@outlook.com",
	packages=find_packages(),
	python_requires=">=3.10",
	include_package_data=True,
	zip_safe=False,
)
