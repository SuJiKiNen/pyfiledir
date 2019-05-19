FROM python:3.6-stretch
SHELL ["/bin/bash", "-c"]
ARG SCRIPT_DIR=/pyfiledir
ARG SOURCE_DIR=.
COPY ${SOURCE_DIR} ${SCRIPT_DIR}
ENV PATH="${SCRIPT_DIR}/bin:${PATH}"
RUN source ${SCRIPT_DIR}/shell/completion.bash
