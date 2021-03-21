import json
import os

f = open('configs_dir/prophet.json')

data = json.load(f)
f.close()

li = [0.05, 0.5, 1, 2]

# for prior_scale in [0.05*val for val in range(1, 40)]:
for prior_scale in li:
    data["model"]["hyperparams"]["prior_scale"] = prior_scale
    os.remove('./configs_dir/prophet.json')
    f = open('configs_dir/prophet.json', 'w+')
    json.dump(data, f, indent=4)
    f.close()
    os.system(r'C:\Users\dhrum\.conda\envs\hmk\python.exe D:/rmds/e2e/e2epipeline.py --config_pth ./configs_dir/prophet.json')

# data["model"]["hyperparams"]["prior_scale"] = 0.05
# data["preprocessor_args"]["end_date"] = "2020-12-30"
#
# f = open('configs_dir/prophet.json', 'w+')
# json.dump(data, f)
# f.close()
# os.system(r'C:\Users\dhrum\.conda\envs\hmk\python.exe D:/rmds/e2e/e2epipeline.py --config_pth ./configs_dir/prophet.json')
