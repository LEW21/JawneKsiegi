set -e

#VERSION=$(git rev-parse HEAD)
VERSION=2
IMAGE=eu.gcr.io/jawne-ksiegi/jk-2015-vagla:$VERSION

find . -name __pycache__ -exec rm {} \; || true
docker build -t $IMAGE .
docker run --entrypoint django-admin $IMAGE test
gcloud docker push $IMAGE
docker run -v `pwd`/static:/app/static --entrypoint django-admin $IMAGE collectstatic --noinput
gsutil -m cp -r `pwd`/static/* gs://eu.artifacts.jawne-ksiegi.appspot.com/django-static/$IMAGE/
gsutil -m acl ch -r -u AllUsers:R gs://eu.artifacts.jawne-ksiegi.appspot.com/django-static/$IMAGE/
