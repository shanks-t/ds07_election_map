## Plotly Dash Chloroplet App

### This app uses data scraped from Opensecrets.org for the 2020 House Elections

### To Run:

1. You need Docker runtime. In the root of the project, build the Docker image:
   ```
   docker build -t election-map .
   ```
2. To run the image built in step 1 as a container:
   ```
   docker run -p 8080:8080 election-map
   ```

This app contains a CI pipeline for deploying to AWS. However, to save costs, this infrastructure has been torn down.




