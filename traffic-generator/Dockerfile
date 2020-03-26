FROM alpine:3.11
RUN apk add --no-cache findutils jq parallel curl
# parallel "echo job {}; curl -s {} | jq '.data | .[\"id\"]'" ::: $(seq 1 20) ::: https://reqres.in/api/users/3 https://reqres.in/api/users/2
ENV EXECUTIONS=10
ENV URL_1="https://reqres.in/api/users/3"
ENV URL_2="https://reqres.in/api/users/2"
ENV JQ_COLORS="1;30:0;37:0;37:0;37:0;32:1;37:1;37"
ENV DELAY=2
ENV SLEEP=5

# CMD parallel "echo job {}; curl -s {} | jq '.data | .[\"id\"]'" ::: $(seq ${EXECUTIONS}) ::: ${URL_1} ${URL_2}
CMD parallel --delay ${DELAY} -j5 --shuf --header : "echo -ne '\033[1mStarting ({#}) \033[0m' ; date; echo -e \"\e[4m\"Execution {f2}\"\e[0m\" -- {f1} && sleep ${SLEEP} && curl -o /dev/null -s -w \"Response Code :: %{http_code}\n\" {f1}; (echo -ne '\033[1mFinishing ({#}) \033[0m' ; date)" ::: f1 ${URL_1} ${URL_2} ::: f2 $(seq ${EXECUTIONS})
# CMD parallel "echo -e \"\e[4m\"job {#}\"\e[0m\" -- {} -- ; curl -s -I -o /dev/null -w \"%{http_code}\" {}; echo -e \ " ::: $(seq ${EXECUTIONS}) ::: ${URL_1} ${URL_2}