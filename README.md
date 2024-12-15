# Steps to setup and run the Project

The repository contains four files namely, Dockerfile, data_loader.py, interface.py and tester.py

To build the docker image using the Dockerfile use:

```bash
docker build --build-arg GITHUB_USERNAME=<Github Username> --build-arg GITHUB_TOKEN=<Github Token> -t <Name of Image>:latest .
```

To create and run the container and the neo4j instance use:

```bash
docker run -d -p 7474:7474 -p 7687:7687 --name <Name of Container> <Name of Image>:latest
```

# Results of the provided testcases

The following Google Drive link contains screenshots of the outputs from the terminal as well as the neo4j browser for all the provided test cases:

[(Google Drive Link)](https://drive.google.com/drive/folders/1hK-UVGPXIgIAMOTVhRPqw86pQqTOKLC2?usp=sharing)