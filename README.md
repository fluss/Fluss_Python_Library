## Publish to PyPi

To publish to PyPi, you need to have a `setup.py` file in the root of your project and use `twine` This file contains all the metadata about your project, such as the name, version, and dependencies. You can create a `setup.py` file by running the following command:

Once a file is created, you can setup

```bash
python setup.py sdist bdist_wheel
```

then:
```bash
twine upload dist/*
```


You will be prompted to enter your PyPi username and password. Oncce uploaded, your package will be available on PyPi for anyone to install using `pip install your-package-name`.

