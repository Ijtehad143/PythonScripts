import sys
import os
import shutil
import random
import argparse

parser = argparse.ArgumentParser(description="Help Information",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-modf", "--module_folder", help="This should be the modules folder path.",
                    default=r"C:\Users\Srinivas.Akkapeddi\source\repos\ploceus\modules")

parser.add_argument("-cfn", "--cloud_folder_name", help="This should be the folder name of your cloud.",
                    default="azure")

parser.add_argument("-modn", "--module_name", help="This should be your module name.",
                    default="advanced_threat_protection")

parser.add_argument("-modv", "--module_version", help="This should be the version of your module.",
                    default="v1.1.0")

parser.add_argument("-tcfn", "--testcase_folder_name", help="This should be the folder name of your test case.",
                    default="example")

parser.add_argument("--subscription_id", help="This should be your subscription id.",
                    default="e0c73eba-77cb-405f-8475-867719cbeaf8")

parser.add_argument("--tenant_id", help="This should be your tenant id.",
                    default="687f51c3-0c5d-4905-84f8-97c683a5b9d1")

args = parser.parse_args()

print("Number of arguments: ", len(sys.argv), "arguments.")
print("Arguments list: ", str(sys.argv))

moduleFolderPath = args.module_folder
cloudName = args.cloud_folder_name
moduleName = args.module_name  # "postgresql_server"
moduleVersion = args.module_version  # "v1.1.0"
testCaseFolderName = args.testcase_folder_name

subscriptionId = args.subscription_id
tenantId = args.tenant_id
resource_name_key = "ploceus"
unique_resource_name = "ploceusqa{}".format(random.randint(10000, 999999))
temp_tag = "QA-Automation"


def replace_line(file_name, line_num, new_text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = new_text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()


def replace_ids(line_content, new_id):
    new_line = "{}= \"{}\"\n".format(line_content.split("=")[0], new_id)
    return new_line


def replace_resource_names(file_name):
    with open(file_name, 'r') as file:
        file_data = file.read()
        file_data = file_data.replace(resource_name_key, unique_resource_name)
        file_data = file_data.replace(temp_tag, "Ploceus-{}".format(temp_tag))
    with open(file_name, 'w') as file:
        file.write(file_data)


# Construct *.tfvars file path
tfvarsFilePath = os.path.join(
    moduleFolderPath, cloudName, moduleName, moduleVersion, testCaseFolderName, "terraform.tfvars")

# Construct *.temp.tfvars file path
tfvarsTempFilePath = os.path.join(
    moduleFolderPath, cloudName, moduleName, moduleVersion, testCaseFolderName, "terraform.temp.tfvars")

# Remove temporary file if it exists
if os.path.exists(tfvarsTempFilePath):
    os.remove(tfvarsTempFilePath)

# Make a copy of the *.tfvars file as *.temp.tfvars
shutil.copy(tfvarsFilePath, tfvarsTempFilePath)

# Read .tfvars file
with open(tfvarsFilePath, 'r') as tfvarsFile:
    if len(tfvarsFile.read(1)) == 0:
        print('FILE IS EMPTY')
    else:
        tfvarsFile.seek(0)

        for lineIndex, line in enumerate(tfvarsFile):

            if "Created_By" in line or "CreatedBy" in line:
                print(line)
                new_line = "{}= \"{}\"\n".format(line.split("=")[0], temp_tag)
                print(new_line)
                replace_line(tfvarsTempFilePath, lineIndex, new_line)

            elif "subscription_id" in line:
                print(line)
                new_line = replace_ids(line, subscriptionId)
                print(new_line)
                replace_line(tfvarsTempFilePath, lineIndex, new_line)

            elif "tenant_id" in line:
                print(line)
                new_line = replace_ids(line, tenantId)
                print(new_line)
                replace_line(tfvarsTempFilePath, lineIndex, new_line)

            elif "/subscriptions/".casefold() in line.casefold():
                items = line.split("=")[1].split("/")

                isSubIdFound = False
                for itemIndex, item in enumerate(items):
                    if isSubIdFound:
                        items[itemIndex] = subscriptionId
                        break
                    if item.casefold() == "subscriptions".casefold():
                        isSubIdFound = True
                        continue
                test = "/".join(items)
                new_line = "{}={}".format(line.split("=")[0], test)
                replace_line(tfvarsTempFilePath, lineIndex, new_line)

# Replace resource names [!Do this only after replacing ids]
replace_resource_names(tfvarsTempFilePath)

os.remove(tfvarsFilePath)
os.rename(tfvarsTempFilePath, tfvarsFilePath)
