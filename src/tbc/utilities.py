import os

import yaml


def create_dir(path):
    try:
        os.makedirs(path)
    except:
        pass


def sep_list_by_mask(x, mask):
    if isinstance(mask, str):
        try:
            mask = [int(m) for m in mask.split(' ')]
        except:
            raise ValueError('Could not convert mask: {} to list of integers!'.format(mask))

    y = []
    n = 0
    for n_in_row in mask:
        to_append = x[n:n + n_in_row]
        if len(to_append) == 0:
            raise ValueError('Bad split mask: {} for list: {}'.format(mask, x))
        y.append(to_append)
        n += n_in_row

    return y


def read_conf(path):
    with open(path) as f:
        conf = yaml.load(f)

    return conf
