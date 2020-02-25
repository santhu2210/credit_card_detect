# contextualsearch

This is GUI solution setup in Docker image. It can used for document level analysis from docx files.

## Instructions to setup:
Run this set of codes on the docker environment/terminal.

1. ```docker login registry.gitlab.com ``` (This is to setup gitlab docker registry in your local machine)
2. ```docker run -itd -p 8005:8000 --name context_copy_edit_server registry.gitlab.com/spiml/contextual_copy_editing:v1```
3. ```docker exec -d context_copy_edit_server bash startapp.sh ```
4. ```docker logout registry.gitlab.com```(To remove login credentials for registry.gitlab.com)

## Run/check GUI
1. open  ```localhost:8005``` / ```your IP address:8005```
2. login using username: admin , password: adminadmin
3. upload docx file (only)
4. check the analysis report with help of charts
5. click the part of chart and see it appropriate high lighted area (the chart heading color and highlighted color are same)