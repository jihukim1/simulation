#Dockerfile
#without an file extension

FROM python
WORKDIR /simulation

COPY . /simulation

RUN pip install --trusted-host pypi.python.org -r requirement.txt

EXPOSE 130

ENV NAME JIHU

CMD ["python", "gq1.py"]
#CMD ["tensorboard", "--logdir=log" ,"--bind_all" ,"--samples_per_plugin=images=100"]