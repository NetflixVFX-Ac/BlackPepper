import xmlrpc.client

# Connect to the HQueue server
hq_sever = xmlrpc.client.ServerProxy("http://192.168.3.103:5000")

try:
    hq_sever.ping()
except ConnectionRefusedError:
    print("HQueue server is not available")

print(hq_sever)
print(hq_sever.ping())




# Define a job that renders an image from an IFD using Mantra.
job_spec = {
    "name": "Render My Image",
    "shell": "bash",
    "command": (
        "cd $HQROOT/houdini_distros/hfs;"
        " source houdini_setup;"
        " mantra < $HQROOT/path/to/ifds/some_frame.ifd"
    )
}
#
#
# job = hq_server.getJob(job_ids[0], ["progress", "status"])
# status = job["status"]
#
# print("The job status is", status)
# if status in hq.getRunningJobStatusNames():
#     print("{:.2f}% complete".format(job["progress"] * 100.0))
#
# job_ids = hq.newjob(job_spec)
#
#
#



# import xmlrpc.client

# Connect to the HQueue client.
# hq_client = xmlrpc.client.ServerProxy("http://hq_client_hostname:5001")