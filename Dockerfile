# Use the Debezium Connect base image
FROM debezium/connect:2.7.3.Final

# Copy the plugin tar.gz file into the container
COPY ./docker/plugins/debezium-connector-postgres-2.7.3.Final-plugin.tar.gz /kafka/connect/

# Extract the tar.gz file
RUN tar xz -C /kafka/connect -f /kafka/connect/debezium-connector-postgres-2.7.3.Final-plugin.tar.gz

# Clean up (optional but recommended to reduce the image size)
RUN rm /kafka/connect/debezium-connector-postgres-2.7.3.Final-plugin.tar.gz
