from setuptools import setup

packages = ['AiBote']

package_data = {
}

install_requires = [
    "loguru~=0.7.0",
    "click==8.1.6",
]

setup_kwargs = {
    'name': 'AiBote.py',
    'version': '1.3.3',
    'description': '...',
    'long_description': '...',
    'long_description_content_type': 'text/markdown',
    'author': 'waitan2018',
    'author_email': None,
    'maintainer': 'waitan2018',
    'maintainer_email': None,
    'url': 'https://github.com/taoshisan/AiBote',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}

setup(**setup_kwargs)
