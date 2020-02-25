import subprocess
import about
version = about.__version__

image_name = "spianalytics/creditcard_detection"
print("--------------------building docker image with the following name: {}:{}------------------------------".format(image_name, version))
subprocess.call(["docker", "build", "--no-cache", "-t", "{}:{}".format(image_name, version), "."])

print("--------------------Manually push the image to docker hub! Remember to sign in to dockerhub before you push!-----------------------")
