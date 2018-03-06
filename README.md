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
                
## Testing locally

make sure the deployer/orig/deployment.yml file doesnt contain:

    resources:
           requests:
             memory: "1Gi"
             cpu: "250m"
           limits:
             memory: "4Gi"
             cpu: "2000m"
         securityContext:
            privileged: true

if it does, remove it for the test time.it limits the resources being used by k8s. for local minikube it fails the tests.
        

## Commands:
>

'deploy'         - deploy to new env
>
* `--image_name            image to deploy, to be used only with command 'deploy' (default=False)`
>
* `--target                Target Namespace for the target ENV`
* `--mongo_uri             Mongo address for deployments log`            
* `--recipe                recipe path (default="")`
* `--deploy-timeout        Deploy timeout, (default=120)`

>

'promote'        - promote from one env to another(currently only from int to stg)
>
* `--target                Target Namespace for the target ENV`
* `--source                Source env to promote from, to be used only with command 'promote' (default=False)`
* `--mongo_uri             Mongo address for deployments log`
* `--git_repository        Repo for swagger`
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

'rollback'         - rollback to previous version
>
* `--target                Target Namespace for the target ENV`
* `--mongo_uri             Mongo address for deployments log`
* `--deploy-timeout        Deploy timeout, (default=120)`
* `--service_name                service name we wish to rollback (default="")`
