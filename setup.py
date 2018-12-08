from setuptools import setup

VERSION = '0.1.1'
DESCRIPTION = "A Python Steem Account Recovery CLI"

if __name__ == "__main__":
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
            'beem',
        ],
        entry_points={
            'console_scripts': [
                'steemrecovery=steemrecovery.steemrecovery:cli',
            ],
        },
        include_package_data=True,
    )
