# Deoply, Promote, Configure, all with this simple tool


[![Build Status](http://drone-io.heed-dev.io/api/badges/heed-dev/deployer/status.svg)](http://drone-io.heed-dev.io/heed-dev/deployer)

## Usage:

```
docker run
       --rm -v /var/run/docker.sock:/var/run/docker.sock
       -e KEY_ID=[AWS_ACCESS_KEY_ID] -e ACCESS_KEY=[AWS_SECRET_ACCESS_KEY]
       -e TARGET_ENV=[int/stg/prod]         
       911479539546.dkr.ecr.us-east-1.amazonaws.com/k8s-deployer
       [command] [options]
```
                
        

Usage:
>
Note: `docker run --rm -v /var/run/docker.sock:/var/run/docker.sock
                -e KEY_ID=${AWS_ACCESS_KEY_ID} -e ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} 
                [image (registry.dnsk.io:5000/agt/k8s-deployer:latest)] 
                [command - (deploy/configure/promote)]
                -e TARGET_ENV=[int/stg/prod]
                [options]



## Commands:
>

'deploy'         - deploy to new env
>
* `--image_name            image to deploy, to be used only with command 'deploy' (default=False)`
>
* `--target                Target Namespace for the target ENV`
* `--git_repository        Repo for services to apply (git.dnsk.io/platform-k8s-config/k8s-services-envs.gi)`
* `--recipe                recipe path (default="")`
* `--deploy-timeout        Deploy timeout, (default=120)`

>

'promote'        - promote from one env to another(currently only from int to stg)
>
* `--target                Target Namespace for the target ENV`
* `--source                Source env to promote from, to be used only with command 'promote' (default=False)`
* `--git_repository        Repo for services to apply (git.dnsk.io/platform-k8s-config/k8s-services-envs.gi)``
* `--deploy-timeout        Deploy timeout, (default=120)`
 

>

'configure'      - configure existing env
>
* `--target                Target Namespace for the target ENV`
* `--git_repository        Repo for services to apply (git.dnsk.io/platform-k8s-config/k8s-services-envs.gi)`

>

'swagger'       - deploy swagger yml to api gateway 
>
* `--yml_path              url to swagger yml`
* `--git_repository        Repo for services to apply (git.dnsk.io/platform-k8s-config/k8s-services-envs.gi)`




