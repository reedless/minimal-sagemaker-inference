# docker build -t minimal_sagemaker_inference:howard -f Dockerfile .
# docker run  -p 8080:8080 --rm --gpus device=all minimal-sagemaker-inference:howard serve
# docker tag minimal_sagemaker_inference:howard 302932544810.dkr.ecr.ap-southeast-1.amazonaws.com/minimal_sagemaker_inference:latest
# docker push 302932544810.dkr.ecr.ap-southeast-1.amazonaws.com/minimal_sagemaker_inference:latest

# since dgx is on cuda 11.7
FROM nvidia/cuda:11.7.1-devel-ubuntu20.04

RUN apt-get update && apt-get install -y \
	python3-pip \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

COPY ./main.py /app/main.py

EXPOSE 8080

ENTRYPOINT ["python3", "main.py"]
