#Dockerfile
#without an file extension

#FROM sjchoi:default
FROM jihu:default

WORKDIR /simulation

COPY . /simulation

RUN pip install --trusted-host pypi.python.org -r requirement.txt

EXPOSE 130

ENV NAME JIHU

# CMD ["python", "ga1.py"]
CMD ["bash"]