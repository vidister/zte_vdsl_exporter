from setuptools import setup

setup(
    name="zte_exporter",
    version="0.1.0",
    py_modules=["zte_exporter"],
    install_requires=[
        "requests",
        "prometheus_client"
    ]
)
