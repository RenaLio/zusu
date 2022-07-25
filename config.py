#coding:utf-8

import os
import shutil
import yaml
# 版本信息等其他信息，使用者无需修改
__version__ ='1.0.0(beta)'

config={
    'version':__version__
}

LOADED = False

if not LOADED:
	if os.path.exists("config.yaml"):
		if os.path.isdir("config.yaml"):
			shutil.rmtree("config.yaml")
			if not os.path.exists("config.example.yaml"):
				raise FileNotFoundError("Default configuraton file not found, please download from the official repo and try again.")
			shutil.copy("config.example.yaml", "config.yaml")
	else:
		if not os.path.exists("config.example.yaml"):
			raise FileNotFoundError("Default configuraton file not found, please download from the official repo and try again.")
		shutil.copy("config.example.yaml", "config.yaml")

	with open("config.yaml", "r", encoding = "utf-8") as f:
		try:
			file_config = yaml.load(f,Loader=yaml.FullLoader)
			config.update(file_config)
		finally:
			pass
	LOADED = True