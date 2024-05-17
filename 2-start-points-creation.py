# Custom Code to create sub-policies
from PIL import Image
from hyperopt.pyll.stochastic import sample
from hyperopt import hp
import random
import augmentations

num_policies = 10
augment_dict = {fn.__name__: (fn, v1, v2) for fn, v1, v2 in augmentations.augment_list()}

space = {
    'policy': hp.choice('policy', list(range(0, len(augment_dict.keys())))),
    'prob': hp.uniform('prob', 0.0, 1.0),
    'level': hp.uniform('level', 0.0, 1.0),
}

image_path = "image.jpg"
image = Image.open(image_path)

def sample_random_params():
    return {key: sample(space[key]) for key in random.sample(space.keys(), k=len(space))}

def get_augment(name):
    return augment_dict[name]

def apply_augment(img, name, level):
    augment_fn, low, high = get_augment(name)
    return augment_fn(img.copy(), level * (high - low) + low)

sub_policies = []
policy_names = list(augment_dict.keys())

for _ in range(num_policies):
    sub_policy = []
    sub_policy.append(sample_random_params())
    sub_policy.append(sample_random_params())
    sub_policies.append(sub_policy)

for i in range(len(sub_policies)):
    ret = apply_augment(image, policy_names[sub_policies[i][0]['policy']], sub_policies[i][0]['level'])
    print(f"First augmented with '{policy_names[sub_policies[i][0]['policy']]}' using magnitude {sub_policies[i][0]['level']}")
    print(f"Consecutively augmented with '{policy_names[sub_policies[i][1]['policy']]}' using magnitude {sub_policies[i][1]['level']}")
    result = apply_augment(ret, policy_names[sub_policies[i][1]['policy']], sub_policies[i][1]['level'])
    result.save(f"augmentations/augmentation-{i}.jpg")