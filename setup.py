from setuptools import setup

VERSION = '0.1.2'
DESCRIPTION = "A Python Steem Account Recovery CLI"


def create_version_file(filename):
    content = "# This file is generated from setup.py.\nVERSION = '%s'\n" % \
              (VERSION)
    with open(filename, 'w') as f:
        f.write(content)


if __name__ == "__main__":
    create_version_file("steemrecovery/version.py")
    setup(
        name='steemrecovery',
        version=VERSION,
        description=DESCRIPTION,
        long_description=DESCRIPTION,
        author='crokkon',
        author_email='crokkon@protonmail.com',
        maintainer='crokkon',
        maintainer_email='crokkon@protonmail.com',
        url='https://github.com/crokkon/steemrecovery',
        keywords=['steem', 'recovery'],
        packages=[
            "steemrecovery",
        ],
        classifiers=[
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Intended Audience :: Financial and Insurance Industry',
            'Topic :: Office/Business :: Financial',
        ],
        install_requires=[
            'beem >= 0.20.14',
        ],
        entry_points={
            'console_scripts': [
                'steemrecovery=steemrecovery.steemrecovery:cli',
            ],
        },
        include_package_data=True,
    )
