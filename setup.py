from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='tbc',
    version='0.1.6',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    test_suite='tbc',
    url='https://github.com/alexeykarnachev/telegram-bot-constructor',
    author='Alexey Karnachev',
    author_email='alekseykarnachev@gmail.com',
    zip_safe=True,
    install_requires=required
)

if __name__ == '__main__':
    pass
